"""
GutIntel Pydantic Models

This package contains all Pydantic models for the GutIntel application,
including core data models and API request/response models.
"""

from .ingredient import (
    # Enums
    EffectDirection,
    EffectStrength,
    BacteriaLevel,
    InteractionType,
    StudyType,
    IngredientCategory,
    
    # Core Models
    IngredientModel,
    MicrobiomeEffectModel,
    MetabolicEffectModel,
    SymptomEffectModel,
    CitationModel,
    IngredientInteractionModel,
    
    # Composite Models
    CompleteIngredientModel,
    IngredientCreateModel,
    IngredientResponseModel,
)

from .api import (
    # API Request Models
    MealAnalysisRequest,
    IngredientSearchRequest,
    EffectSearchRequest,
    CitationRequest,
    InteractionRequest,
    HealthMetricsRequest,
    BatchOperationRequest,
    
    # API Response Models
    MealAnalysisResponse,
    IngredientSearchResponse,
    EffectSearchResponse,
    HealthMetricsResponse,
    BatchOperationResponse,
    
    # Supporting Models
    IngredientInsight,
    InteractionInsight,
    EffectSummary,
    PaginationMetadata,
    ErrorResponse,
    SuccessResponse,
    
    # Enums
    SortOrder,
    IngredientSortField,
)

__all__ = [
    # Enums
    "EffectDirection",
    "EffectStrength",
    "BacteriaLevel",
    "InteractionType",
    "StudyType",
    "IngredientCategory",
    "SortOrder",
    "IngredientSortField",
    
    # Core Models
    "IngredientModel",
    "MicrobiomeEffectModel",
    "MetabolicEffectModel",
    "SymptomEffectModel",
    "CitationModel",
    "IngredientInteractionModel",
    
    # Composite Models
    "CompleteIngredientModel",
    "IngredientCreateModel",
    "IngredientResponseModel",
    
    # API Request Models
    "MealAnalysisRequest",
    "IngredientSearchRequest",
    "EffectSearchRequest",
    "CitationRequest",
    "InteractionRequest",
    "HealthMetricsRequest",
    "BatchOperationRequest",
    
    # API Response Models
    "MealAnalysisResponse",
    "IngredientSearchResponse",
    "EffectSearchResponse",
    "HealthMetricsResponse",
    "BatchOperationResponse",
    
    # Supporting Models
    "IngredientInsight",
    "InteractionInsight",
    "EffectSummary",
    "PaginationMetadata",
    "ErrorResponse",
    "SuccessResponse",
]