"""
API request and response models for GutIntel.

This module contains Pydantic models specifically designed for API interactions,
including request validation, response formatting, and pagination.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .ingredient import (
    IngredientCategory, EffectDirection, EffectStrength, 
    InteractionType, StudyType, IngredientResponseModel
)


class SortOrder(str, Enum):
    """Sort order for API responses."""
    ASC = "asc"
    DESC = "desc"


class IngredientSortField(str, Enum):
    """Fields available for sorting ingredients."""
    NAME = "name"
    GUT_SCORE = "gut_score"
    CONFIDENCE_SCORE = "confidence_score"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class MealAnalysisRequest(BaseModel):
    """
    Request model for meal analysis API.
    
    Analyzes a list of ingredients to provide gut health insights.
    
    Example:
        >>> request = MealAnalysisRequest(
        ...     ingredients=["yogurt", "banana", "oats"],
        ...     portion_sizes={"yogurt": "1 cup", "banana": "1 medium", "oats": "0.5 cup"},
        ...     user_preferences={"avoid_dairy": False, "high_fiber": True}
        ... )
    """
    ingredients: List[str] = Field(..., min_items=1, max_items=50)
    portion_sizes: Optional[Dict[str, str]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    include_interactions: bool = True
    include_dosage_recommendations: bool = True

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        """Validate ingredient list."""
        if not v:
            raise ValueError('At least one ingredient is required')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_ingredients = []
        for ingredient in v:
            if ingredient.lower() not in seen:
                seen.add(ingredient.lower())
                unique_ingredients.append(ingredient.strip())
        
        return unique_ingredients

    @field_validator('portion_sizes')
    @classmethod
    def validate_portion_sizes(cls, v, info):
        """Validate portion sizes match ingredients."""
        if v is not None:
            ingredients = info.data.get('ingredients', [])
            for ingredient in v.keys():
                if ingredient not in ingredients:
                    raise ValueError(f'Portion size specified for unknown ingredient: {ingredient}')
        return v


class IngredientInsight(BaseModel):
    """Individual ingredient insight for meal analysis."""
    name: str
    slug: str
    category: IngredientCategory
    gut_score: Optional[float] = None
    confidence_score: Optional[float] = None
    contribution_score: float = Field(..., ge=0, le=10)
    key_benefits: List[str] = Field(default_factory=list)
    potential_concerns: List[str] = Field(default_factory=list)
    dosage_recommendation: Optional[str] = None

    class Config:
        use_enum_values = True


class InteractionInsight(BaseModel):
    """Interaction insight between ingredients."""
    ingredient_1: str
    ingredient_2: str
    interaction_type: InteractionType
    effect_description: Optional[str] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None

    class Config:
        use_enum_values = True


class MealAnalysisResponse(BaseModel):
    """
    Response model for meal analysis API.
    
    Provides comprehensive gut health analysis of a meal.
    
    Example:
        >>> response = MealAnalysisResponse(
        ...     overall_gut_score=7.8,
        ...     confidence_score=0.85,
        ...     analysis_summary="This meal provides excellent gut health benefits...",
        ...     ingredient_insights=[insight1, insight2],
        ...     interaction_insights=[interaction1],
        ...     recommendations=["Consider adding fermented foods", "Increase fiber intake"]
        ... )
    """
    overall_gut_score: float = Field(..., ge=0, le=10)
    confidence_score: float = Field(..., ge=0, le=1)
    analysis_summary: str
    ingredient_insights: List[IngredientInsight]
    interaction_insights: List[InteractionInsight] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    microbiome_impact: Optional[Dict[str, Any]] = None
    metabolic_impact: Optional[Dict[str, Any]] = None
    symptom_impact: Optional[Dict[str, Any]] = None
    analyzed_at: datetime = Field(default_factory=datetime.now)

    @field_validator('overall_gut_score')
    @classmethod
    def validate_overall_gut_score(cls, v):
        """Round gut score to 1 decimal place."""
        return round(v, 1)

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        """Round confidence score to 2 decimal places."""
        return round(v, 2)


class IngredientSearchRequest(BaseModel):
    """
    Request model for ingredient search API.
    
    Provides flexible search and filtering capabilities.
    
    Example:
        >>> request = IngredientSearchRequest(
        ...     query="probiotic",
        ...     categories=[IngredientCategory.PROBIOTIC],
        ...     min_gut_score=7.0,
        ...     max_gut_score=10.0,
        ...     sort_by=IngredientSortField.GUT_SCORE,
        ...     sort_order=SortOrder.DESC,
        ...     page=1,
        ...     page_size=20
        ... )
    """
    query: Optional[str] = Field(None, min_length=1, max_length=100)
    categories: Optional[List[IngredientCategory]] = None
    min_gut_score: Optional[float] = Field(None, ge=0, le=10)
    max_gut_score: Optional[float] = Field(None, ge=0, le=10)
    min_confidence_score: Optional[float] = Field(None, ge=0, le=1)
    max_confidence_score: Optional[float] = Field(None, ge=0, le=1)
    has_effects: Optional[bool] = None
    has_citations: Optional[bool] = None
    sort_by: IngredientSortField = IngredientSortField.NAME
    sort_order: SortOrder = SortOrder.ASC
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @field_validator('min_gut_score', 'max_gut_score')
    @classmethod
    def validate_gut_scores(cls, v):
        """Round gut scores to 1 decimal place."""
        if v is not None:
            return round(v, 1)
        return v

    @field_validator('min_confidence_score', 'max_confidence_score')
    @classmethod
    def validate_confidence_scores(cls, v):
        """Round confidence scores to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    @field_validator('max_gut_score')
    @classmethod
    def validate_gut_score_range(cls, v, info):
        """Validate gut score range."""
        min_score = info.data.get('min_gut_score')
        if v is not None and min_score is not None:
            if v < min_score:
                raise ValueError('max_gut_score must be greater than or equal to min_gut_score')
        return v

    @field_validator('max_confidence_score')
    @classmethod
    def validate_confidence_score_range(cls, v, info):
        """Validate confidence score range."""
        min_score = info.data.get('min_confidence_score')
        if v is not None and min_score is not None:
            if v < min_score:
                raise ValueError('max_confidence_score must be greater than or equal to min_confidence_score')
        return v

    class Config:
        use_enum_values = True


class PaginationMetadata(BaseModel):
    """Pagination metadata for API responses."""
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total_items: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)
    has_next: bool
    has_previous: bool

    @field_validator('total_pages')
    @classmethod
    def calculate_total_pages(cls, v, info):
        """Calculate total pages from total items and page size."""
        total_items = info.data.get('total_items', 0)
        page_size = info.data.get('page_size', 20)
        return max(1, (total_items + page_size - 1) // page_size)

    @field_validator('has_next')
    @classmethod
    def calculate_has_next(cls, v, info):
        """Calculate if there's a next page."""
        page = info.data.get('page', 1)
        total_pages = info.data.get('total_pages', 1)
        return page < total_pages

    @field_validator('has_previous')
    @classmethod
    def calculate_has_previous(cls, v, info):
        """Calculate if there's a previous page."""
        page = info.data.get('page', 1)
        return page > 1


class IngredientSearchResponse(BaseModel):
    """
    Response model for ingredient search API.
    
    Provides paginated search results with metadata.
    
    Example:
        >>> response = IngredientSearchResponse(
        ...     ingredients=[ingredient1, ingredient2],
        ...     pagination=PaginationMetadata(
        ...         page=1, page_size=20, total_items=45, 
        ...         total_pages=3, has_next=True, has_previous=False
        ...     ),
        ...     search_metadata={"query": "probiotic", "filters_applied": 2}
        ... )
    """
    ingredients: List[IngredientResponseModel]
    pagination: PaginationMetadata
    search_metadata: Optional[Dict[str, Any]] = None
    search_time_ms: Optional[int] = None


class EffectSearchRequest(BaseModel):
    """Request model for searching ingredient effects."""
    ingredient_id: Optional[UUID] = None
    effect_types: Optional[List[str]] = Field(None, description="microbiome, metabolic, symptom")
    effect_strength: Optional[List[EffectStrength]] = None
    effect_direction: Optional[List[EffectDirection]] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    bacteria_name: Optional[str] = None
    symptom_name: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @field_validator('effect_types')
    @classmethod
    def validate_effect_types(cls, v):
        """Validate effect types."""
        if v is not None:
            valid_types = {'microbiome', 'metabolic', 'symptom'}
            for effect_type in v:
                if effect_type not in valid_types:
                    raise ValueError(f'Invalid effect type: {effect_type}')
        return v

    @field_validator('min_confidence')
    @classmethod
    def validate_min_confidence(cls, v):
        """Round confidence to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        use_enum_values = True


class EffectSummary(BaseModel):
    """Summary of an effect for API responses."""
    id: UUID
    effect_type: str
    effect_name: str
    effect_strength: EffectStrength
    effect_direction: Optional[EffectDirection] = None
    bacteria_level: Optional[str] = None
    confidence: Optional[float] = None
    mechanism: Optional[str] = None

    class Config:
        use_enum_values = True


class EffectSearchResponse(BaseModel):
    """Response model for effect search API."""
    effects: List[EffectSummary]
    pagination: PaginationMetadata
    search_metadata: Optional[Dict[str, Any]] = None


class CitationRequest(BaseModel):
    """Request model for citation operations."""
    pmid: Optional[str] = Field(None, max_length=20)
    doi: Optional[str] = Field(None, max_length=255)
    title: str = Field(..., min_length=1)
    authors: str = Field(..., min_length=1)
    journal: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1900, le=2025)
    study_type: StudyType
    sample_size: Optional[int] = Field(None, gt=0)
    study_quality: Optional[float] = Field(None, ge=0, le=1)

    @field_validator('pmid')
    @classmethod
    def validate_pmid(cls, v):
        """Validate PMID format."""
        if v is not None:
            import re
            if not re.match(r'^\d{1,8}$', v):
                raise ValueError('PMID must be 1-8 digits')
        return v

    @field_validator('study_quality')
    @classmethod
    def validate_study_quality(cls, v):
        """Round study quality to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        use_enum_values = True


class InteractionRequest(BaseModel):
    """Request model for ingredient interactions."""
    ingredient_1_id: UUID
    ingredient_2_id: UUID
    interaction_type: InteractionType
    effect_description: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Round confidence to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    @field_validator('ingredient_2_id')
    @classmethod
    def validate_different_ingredients(cls, v, info):
        """Ensure ingredients are different."""
        ingredient_1_id = info.data.get('ingredient_1_id')
        if ingredient_1_id and v == ingredient_1_id:
            raise ValueError('Ingredients cannot interact with themselves')
        return v

    class Config:
        use_enum_values = True


class HealthMetricsRequest(BaseModel):
    """Request model for health metrics analysis."""
    ingredients: List[str] = Field(..., min_items=1, max_items=20)
    time_period: Optional[str] = Field("daily", pattern=r'^(daily|weekly|monthly)$')
    include_microbiome: bool = True
    include_metabolic: bool = True
    include_symptoms: bool = True
    user_profile: Optional[Dict[str, Any]] = None

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        """Validate and clean ingredient list."""
        if not v:
            raise ValueError('At least one ingredient is required')
        
        # Remove duplicates and empty strings
        cleaned = []
        seen = set()
        for ingredient in v:
            ingredient = ingredient.strip()
            if ingredient and ingredient.lower() not in seen:
                seen.add(ingredient.lower())
                cleaned.append(ingredient)
        
        return cleaned


class HealthMetricsResponse(BaseModel):
    """Response model for health metrics analysis."""
    overall_score: float = Field(..., ge=0, le=10)
    microbiome_score: Optional[float] = Field(None, ge=0, le=10)
    metabolic_score: Optional[float] = Field(None, ge=0, le=10)
    symptom_score: Optional[float] = Field(None, ge=0, le=10)
    confidence: float = Field(..., ge=0, le=1)
    
    detailed_analysis: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    
    analyzed_at: datetime = Field(default_factory=datetime.now)

    @field_validator('overall_score', 'microbiome_score', 'metabolic_score', 'symptom_score')
    @classmethod
    def validate_scores(cls, v):
        """Round scores to 1 decimal place."""
        if v is not None:
            return round(v, 1)
        return v

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Round confidence to 2 decimal places."""
        return round(v, 2)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Standard success response model."""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class BatchOperationRequest(BaseModel):
    """Request model for batch operations."""
    operation: str = Field(..., pattern=r'^(create|update|delete)$')
    items: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    validation_only: bool = False

    @field_validator('items')
    @classmethod
    def validate_items_limit(cls, v):
        """Validate batch size limits."""
        if len(v) > 100:
            raise ValueError('Batch operations are limited to 100 items')
        return v


class BatchOperationResponse(BaseModel):
    """Response model for batch operations."""
    operation: str
    total_items: int
    successful_items: int
    failed_items: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)