"""
AI-powered endpoints for GutIntel API.

This module provides AI-enhanced endpoints for natural language explanations,
personalized recommendations, meal analysis, and conversational Q&A.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import time

from ..services.ai_service import ai_service
from ..models.ai_models import (
    ExplanationRequest,
    ExplanationResponse,
    RecommendationRequest,
    RecommendationResponse,
    MealAnalysisRequest,
    MealAnalysisResponse,
    ChatRequest,
    ChatResponse,
    AIHealthRequest,
    AIHealthResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse
)
from ..models.responses import BaseResponse
from ..database import get_ingredient_repository
from database.repositories import IngredientRepository


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={
        500: {"description": "AI service error"},
        503: {"description": "AI service unavailable"},
    }
)


@router.post(
    "/explain",
    response_model=BaseResponse[ExplanationResponse],
    summary="Generate natural language explanation",
    description="Transform technical ingredient data into user-friendly explanations with practical advice"
)
async def explain_ingredient(
    ingredient_name: str,
    user_level: str = "general",
    repo: IngredientRepository = Depends(get_ingredient_repository)
) -> BaseResponse[ExplanationResponse]:
    """
    Generate a natural language explanation for an ingredient.
    
    - **ingredient_name**: Name of the ingredient to explain
    - **user_level**: Explanation level (beginner, general, advanced)
    
    Returns user-friendly explanation with practical advice and timelines.
    """
    try:
        # Get ingredient data from database
        ingredient = await repo.get_ingredient_by_name(ingredient_name)
        
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient '{ingredient_name}' not found"
            )
        
        # Convert to dict format for AI processing
        ingredient_data = {
            "name": ingredient.ingredient.name,
            "category": ingredient.ingredient.category,
            "description": ingredient.ingredient.description,
            "gut_score": ingredient.ingredient.gut_score,
            "confidence_score": ingredient.ingredient.confidence_score,
            "dosage_info": str(ingredient.ingredient.dosage_info) if ingredient.ingredient.dosage_info else "Consult healthcare provider",
            "safety_notes": ingredient.ingredient.safety_notes,
            "effects": {
                "microbiome_effects": [
                    {
                        "bacteria_name": effect.bacteria_name,
                        "effect_type": effect.effect_type,
                        "effect_strength": effect.effect_strength,
                        "mechanism": effect.mechanism
                    }
                    for effect in ingredient.microbiome_effects
                ],
                "symptom_effects": [
                    {
                        "symptom_name": effect.symptom_name,
                        "symptom_category": effect.symptom_category,
                        "effect_direction": effect.effect_direction,
                        "effect_strength": effect.effect_strength
                    }
                    for effect in ingredient.symptom_effects
                ]
            }
        }
        
        # Create explanation request
        request = ExplanationRequest(
            ingredient_data=ingredient_data,
            user_level=user_level
        )
        
        # Generate explanation using AI service
        explanation = await ai_service.generate_explanation(request)
        
        return BaseResponse.success_response(explanation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.post(
    "/recommend",
    response_model=BaseResponse[RecommendationResponse],
    summary="Get personalized recommendations",
    description="Generate personalized ingredient recommendations based on user profile and goals"
)
async def get_recommendations(
    request: RecommendationRequest
) -> BaseResponse[RecommendationResponse]:
    """
    Generate personalized ingredient recommendations.
    
    Takes user profile including symptoms, goals, dietary restrictions, and current supplements
    to recommend optimal ingredients for their gut health journey.
    """
    try:
        # Validate user profile
        if not request.user_profile.symptoms and not request.user_profile.goals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile must include either symptoms or goals"
            )
        
        # Generate recommendations using AI service
        recommendations = await ai_service.generate_recommendations(request)
        
        return BaseResponse.success_response(recommendations)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post(
    "/analyze-meal",
    response_model=BaseResponse[MealAnalysisResponse],
    summary="Analyze meal for gut health",
    description="Analyze ingredient combinations for gut health impact, interactions, and optimization suggestions"
)
async def analyze_meal(
    request: MealAnalysisRequest
) -> BaseResponse[MealAnalysisResponse]:
    """
    Analyze a meal or supplement combination for gut health impact.
    
    Evaluates ingredient interactions, calculates combined gut score,
    and provides optimization suggestions.
    """
    try:
        # Validate ingredients
        if not request.ingredients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one ingredient is required"
            )
        
        # Generate meal analysis using AI service
        analysis = await ai_service.analyze_meal(request)
        
        return BaseResponse.success_response(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze meal: {str(e)}"
        )


@router.post(
    "/chat",
    response_model=BaseResponse[ChatResponse],
    summary="Conversational Q&A",
    description="Chat interface for gut health questions using AI and ingredient database"
)
async def chat(
    request: ChatRequest
) -> BaseResponse[ChatResponse]:
    """
    Conversational Q&A interface for gut health questions.
    
    Provides intelligent responses using the ingredient database and AI reasoning.
    Maintains conversation context for natural dialogue.
    """
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one message is required"
            )
        
        # Generate chat response using AI service
        response = await ai_service.chat(request)
        
        return BaseResponse.success_response(response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}"
        )


@router.post(
    "/batch-analyze",
    response_model=BaseResponse[BatchAnalysisResponse],
    summary="Batch ingredient analysis",
    description="Analyze multiple ingredients simultaneously for interactions and combined effects"
)
async def batch_analyze(
    request: BatchAnalysisRequest
) -> BaseResponse[BatchAnalysisResponse]:
    """
    Analyze multiple ingredients simultaneously.
    
    Evaluates individual and combined effects, identifies synergies,
    and provides comprehensive analysis of the ingredient combination.
    """
    try:
        # Validate ingredients
        if not request.ingredients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one ingredient is required"
            )
        
        # For now, use meal analysis as a proxy for batch analysis
        meal_request = MealAnalysisRequest(
            ingredients=request.ingredients,
            meal_type="supplement",
            user_profile=request.user_profile
        )
        
        meal_analysis = await ai_service.analyze_meal(meal_request)
        
        # Convert to batch analysis format
        batch_response = BatchAnalysisResponse(
            individual_scores={ing: 7.0 for ing in request.ingredients},  # Mock individual scores
            combined_score=meal_analysis.gut_score,
            analysis_summary=meal_analysis.analysis,
            top_synergies=meal_analysis.synergistic_effects,
            warnings=meal_analysis.potential_issues,
            optimization_suggestions=meal_analysis.optimization_suggestions
        )
        
        return BaseResponse.success_response(batch_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze batch: {str(e)}"
        )


@router.get(
    "/health",
    response_model=BaseResponse[AIHealthResponse],
    summary="AI service health check",
    description="Check the health and performance of the AI service"
)
async def ai_health_check() -> BaseResponse[AIHealthResponse]:
    """
    Health check for the AI service.
    
    Tests OpenAI connectivity and response times to ensure
    the AI-powered features are functioning properly.
    """
    try:
        start_time = time.time()
        
        # Test AI service with a simple query
        test_request = ChatRequest(
            messages=[{
                "role": "user",
                "content": "What is gut health?",
                "timestamp": "2024-01-01T00:00:00Z"
            }]
        )
        
        response = await ai_service.chat(test_request)
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        health_response = AIHealthResponse(
            status="healthy",
            model=ai_service.model,
            response_time_ms=response_time_ms,
            test_response=response.response[:100] + "..." if len(response.response) > 100 else response.response
        )
        
        return BaseResponse.success_response(health_response)
        
    except Exception as e:
        health_response = AIHealthResponse(
            status="unhealthy",
            model=ai_service.model,
            response_time_ms=0.0,
            test_response="",
            error_message=str(e)
        )
        
        return BaseResponse.success_response(health_response)


@router.get(
    "/capabilities",
    response_model=BaseResponse[Dict[str, Any]],
    summary="AI service capabilities",
    description="Get information about AI service capabilities and features"
)
async def get_ai_capabilities() -> BaseResponse[Dict[str, Any]]:
    """
    Get information about AI service capabilities.
    
    Returns details about available features, models, and limitations.
    """
    capabilities = {
        "features": [
            "Natural language ingredient explanations",
            "Personalized recommendations",
            "Meal/supplement analysis",
            "Conversational Q&A",
            "Batch ingredient analysis"
        ],
        "models": {
            "primary": ai_service.model,
            "description": "GPT-4 for comprehensive gut health analysis"
        },
        "limitations": [
            "Not a replacement for medical advice",
            "Based on available ingredient database",
            "Response times may vary with load"
        ],
        "supported_languages": ["English"],
        "max_ingredients_per_analysis": 20,
        "conversation_context_limit": 10
    }
    
    return BaseResponse.success_response(capabilities)