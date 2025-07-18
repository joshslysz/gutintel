"""
Ingredient API routes for GutIntel application.

This module provides REST API endpoints for ingredient data access,
including list, retrieve, and search operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID

from database.repositories import IngredientRepository
from models.ingredient import IngredientModel, CompleteIngredientModel
from ..database import get_ingredient_repository
from ..models.responses import (
    BaseResponse, 
    PaginatedResponse, 
    NotFoundErrorResponse,
    InternalServerErrorResponse,
    ValidationErrorResponse,
    ResponseMetadata
)


router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"],
    responses={
        404: {"description": "Ingredient not found"},
        500: {"description": "Internal server error"},
    }
)


@router.get(
    "/",
    response_model=PaginatedResponse[dict],
    summary="List ingredients",
    description="Get a paginated list of ingredients with optional filtering"
)
async def list_ingredients(
    category: Optional[str] = Query(None, description="Filter by ingredient category"),
    min_gut_score: Optional[float] = Query(None, ge=0, le=10, description="Minimum gut score"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    repo: IngredientRepository = Depends(get_ingredient_repository)
) -> PaginatedResponse[dict]:
    """
    List ingredients with optional filtering and pagination.
    
    - **category**: Filter by ingredient category (probiotic, prebiotic, etc.)
    - **min_gut_score**: Minimum gut score threshold (0-10)
    - **page**: Page number for pagination
    - **per_page**: Number of items per page (max 100)
    """
    try:
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Get ingredients with filters
        ingredients = await repo.search_ingredients(
            category=category,
            min_gut_score=min_gut_score,
            limit=per_page,
            offset=offset
        )
        
        # Convert to dict format for response
        ingredient_data = []
        for ingredient in ingredients:
            ingredient_dict = {
                "id": str(ingredient.id),
                "name": ingredient.name,
                "slug": ingredient.slug,
                "category": ingredient.category,
                "description": ingredient.description,
                "gut_score": ingredient.gut_score,
                "confidence_score": ingredient.confidence_score,
                "last_updated": ingredient.updated_at.isoformat()
            }
            ingredient_data.append(ingredient_dict)
        
        # For simplicity, we'll estimate total from current results
        # In production, you'd want a separate count query
        total = len(ingredients) if len(ingredients) < per_page else (page * per_page) + 1
        
        return PaginatedResponse.create(
            data=ingredient_data,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list ingredients: {str(e)}"
        )


@router.get(
    "/{ingredient_name}",
    response_model=BaseResponse[dict],
    summary="Get ingredient by name",
    description="Get detailed information about a specific ingredient by name"
)
async def get_ingredient(
    ingredient_name: str,
    repo: IngredientRepository = Depends(get_ingredient_repository)
) -> BaseResponse[dict]:
    """
    Get detailed ingredient information by name.
    
    - **ingredient_name**: Name of the ingredient to retrieve
    
    Returns complete ingredient data including all effects and citations.
    """
    try:
        # Get ingredient by name
        ingredient = await repo.get_ingredient_by_name(ingredient_name)
        
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient '{ingredient_name}' not found"
            )
        
        # Convert to dict format for response
        ingredient_data = {
            "id": str(ingredient.ingredient.id),
            "name": ingredient.ingredient.name,
            "slug": ingredient.ingredient.slug,
            "aliases": ingredient.ingredient.aliases,
            "category": ingredient.ingredient.category,
            "description": ingredient.ingredient.description,
            "gut_score": ingredient.ingredient.gut_score,
            "confidence_score": ingredient.ingredient.confidence_score,
            "dosage_info": ingredient.ingredient.dosage_info,
            "safety_notes": ingredient.ingredient.safety_notes,
            "effects": {
                "microbiome_effects": [
                    {
                        "bacteria_name": effect.bacteria_name,
                        "bacteria_level": effect.bacteria_level,
                        "effect_type": effect.effect_type,
                        "effect_strength": effect.effect_strength,
                        "confidence": effect.confidence,
                        "mechanism": effect.mechanism
                    }
                    for effect in ingredient.microbiome_effects
                ],
                "metabolic_effects": [
                    {
                        "effect_name": effect.effect_name,
                        "effect_category": effect.effect_category,
                        "impact_direction": effect.impact_direction,
                        "effect_strength": effect.effect_strength,
                        "confidence": effect.confidence,
                        "dosage_dependent": effect.dosage_dependent,
                        "mechanism": effect.mechanism
                    }
                    for effect in ingredient.metabolic_effects
                ],
                "symptom_effects": [
                    {
                        "symptom_name": effect.symptom_name,
                        "symptom_category": effect.symptom_category,
                        "effect_direction": effect.effect_direction,
                        "effect_strength": effect.effect_strength,
                        "confidence": effect.confidence,
                        "dosage_dependent": effect.dosage_dependent,
                        "population_notes": effect.population_notes
                    }
                    for effect in ingredient.symptom_effects
                ]
            },
            "citations": [
                {
                    "title": citation.title,
                    "authors": citation.authors,
                    "journal": citation.journal,
                    "publication_year": citation.publication_year,
                    "study_type": citation.study_type,
                    "pmid": citation.pmid,
                    "doi": citation.doi
                }
                for citation in ingredient.citations
            ],
            "summary": {
                "total_effects": ingredient.total_effects_count,
                "average_confidence": ingredient.average_confidence,
                "citations_count": len(ingredient.citations)
            },
            "last_updated": ingredient.ingredient.updated_at.isoformat()
        }
        
        return BaseResponse.success_response(ingredient_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ingredient: {str(e)}"
        )


@router.get(
    "/search/bacteria/{bacteria_name}",
    response_model=BaseResponse[List[dict]],
    summary="Search ingredients by bacteria",
    description="Find ingredients that affect a specific type of bacteria"
)
async def search_by_bacteria(
    bacteria_name: str,
    repo: IngredientRepository = Depends(get_ingredient_repository)
) -> BaseResponse[List[dict]]:
    """
    Search ingredients by bacteria name they affect.
    
    - **bacteria_name**: Name of the bacteria to search for (partial matches allowed)
    
    Returns ingredients that have documented effects on the specified bacteria.
    """
    try:
        # Validate bacteria name
        if not bacteria_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bacteria name cannot be empty"
            )
        
        # Search ingredients by bacteria
        ingredients = await repo.search_by_bacteria(bacteria_name)
        
        # Convert to dict format for response
        ingredient_data = [
            {
                "id": str(ingredient.id),
                "name": ingredient.name,
                "slug": ingredient.slug,
                "category": ingredient.category,
                "gut_score": ingredient.gut_score,
                "confidence_score": ingredient.confidence_score,
                "description": ingredient.description
            }
            for ingredient in ingredients
        ]
        
        return BaseResponse.success_response(ingredient_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search by bacteria: {str(e)}"
        )


@router.get(
    "/high-confidence",
    response_model=BaseResponse[List[dict]],
    summary="Get high-confidence ingredients",
    description="Get ingredients with high confidence scores"
)
async def get_high_confidence_ingredients(
    min_confidence: float = Query(0.8, ge=0, le=1, description="Minimum confidence score"),
    repo: IngredientRepository = Depends(get_ingredient_repository)
) -> BaseResponse[List[dict]]:
    """
    Get ingredients with high confidence scores.
    
    - **min_confidence**: Minimum confidence score (0-1, default: 0.8)
    
    Returns ingredients that meet the confidence threshold.
    """
    try:
        # Get high confidence ingredients
        ingredients = await repo.get_high_confidence_ingredients(min_confidence)
        
        # Convert to dict format for response
        ingredient_data = [
            {
                "id": str(ingredient.id),
                "name": ingredient.name,
                "slug": ingredient.slug,
                "category": ingredient.category,
                "gut_score": ingredient.gut_score,
                "confidence_score": ingredient.confidence_score,
                "description": ingredient.description
            }
            for ingredient in ingredients
        ]
        
        return BaseResponse.success_response(ingredient_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get high confidence ingredients: {str(e)}"
        )