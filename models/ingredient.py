"""
Core Pydantic models for GutIntel ingredient data.

This module contains the primary data models that mirror the database schema,
including validation rules and custom validators for gut health data.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator
import re


class EffectDirection(str, Enum):
    """Direction of health effect."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EffectStrength(str, Enum):
    """Strength of health effect."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class BacteriaLevel(str, Enum):
    """Type of bacterial level change."""
    INCREASE = "increase"
    DECREASE = "decrease"
    MODULATE = "modulate"


class InteractionType(str, Enum):
    """Type of ingredient interaction."""
    SYNERGISTIC = "synergistic"
    ANTAGONISTIC = "antagonistic"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class StudyType(str, Enum):
    """Type of scientific study."""
    RCT = "rct"
    OBSERVATIONAL = "observational"
    META_ANALYSIS = "meta_analysis"
    REVIEW = "review"
    CASE_STUDY = "case_study"
    IN_VITRO = "in_vitro"
    ANIMAL = "animal"


class IngredientCategory(str, Enum):
    """Category of ingredient."""
    PROBIOTIC = "probiotic"
    PREBIOTIC = "prebiotic"
    POSTBIOTIC = "postbiotic"
    FIBER = "fiber"
    POLYPHENOL = "polyphenol"
    FATTY_ACID = "fatty_acid"
    VITAMIN = "vitamin"
    MINERAL = "mineral"
    HERB = "herb"
    OTHER = "other"


class BaseTimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IngredientModel(BaseTimestampedModel):
    """
    Core ingredient model with gut health scoring.
    
    Represents a single ingredient with its basic properties, gut health score,
    and dosage information. This model mirrors the ingredients table structure.
    
    Example:
        >>> ingredient = IngredientModel(
        ...     name="Lactobacillus acidophilus",
        ...     slug="lactobacillus-acidophilus",
        ...     category=IngredientCategory.PROBIOTIC,
        ...     gut_score=8.5,
        ...     confidence_score=0.85,
        ...     dosage_info={"min_cfu": 1000000000, "max_cfu": 10000000000}
        ... )
    """
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    aliases: List[str] = Field(default_factory=list)
    category: IngredientCategory
    description: Optional[str] = None
    gut_score: Optional[float] = Field(None, ge=0, le=10)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    dosage_info: Optional[Dict[str, Any]] = None
    safety_notes: Optional[str] = None

    @field_validator('gut_score')
    @classmethod
    def validate_gut_score(cls, v):
        """Validate gut score is between 0 and 10 with one decimal place."""
        if v is not None:
            if not (0 <= v <= 10):
                raise ValueError('gut_score must be between 0 and 10')
            # Round to 1 decimal place
            return round(v, 1)
        return v

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        """Validate confidence score is between 0 and 1 with two decimal places."""
        if v is not None:
            if not (0 <= v <= 1):
                raise ValueError('confidence_score must be between 0 and 1')
            # Round to 2 decimal places
            return round(v, 2)
        return v

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format (lowercase, hyphens, alphanumeric)."""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('slug must contain only lowercase letters, numbers, and hyphens')
        return v

    @field_validator('dosage_info')
    @classmethod
    def validate_dosage_info(cls, v):
        """Validate dosage information structure."""
        if v is not None:
            # Check for common dosage fields
            valid_keys = {
                'min_dose', 'max_dose', 'unit', 'frequency', 'duration',
                'min_cfu', 'max_cfu', 'form', 'timing', 'notes'
            }
            for key in v.keys():
                if key not in valid_keys:
                    raise ValueError(f'Invalid dosage_info key: {key}')
        return v

    class Config:
        use_enum_values = True
        validate_assignment = True


class MicrobiomeEffectModel(BaseTimestampedModel):
    """
    Model for microbiome effects on gut bacteria.
    
    Represents how an ingredient affects specific gut bacteria populations.
    
    Example:
        >>> effect = MicrobiomeEffectModel(
        ...     ingredient_id=ingredient.id,
        ...     bacteria_name="Bifidobacterium longum",
        ...     bacteria_level=BacteriaLevel.INCREASE,
        ...     effect_strength=EffectStrength.MODERATE,
        ...     confidence=0.75
        ... )
    """
    id: UUID = Field(default_factory=uuid4)
    ingredient_id: UUID
    bacteria_name: str = Field(..., min_length=1, max_length=255)
    bacteria_level: BacteriaLevel
    effect_type: Optional[str] = Field(None, max_length=100)
    effect_strength: EffectStrength
    confidence: Optional[float] = Field(None, ge=0, le=1)
    mechanism: Optional[str] = None

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Round confidence to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        use_enum_values = True


class MetabolicEffectModel(BaseTimestampedModel):
    """
    Model for metabolic effects of ingredients.
    
    Represents metabolic impacts like SCFA production, inflammation effects.
    
    Example:
        >>> effect = MetabolicEffectModel(
        ...     ingredient_id=ingredient.id,
        ...     effect_name="Butyrate production",
        ...     effect_category="metabolism",
        ...     impact_direction=EffectDirection.POSITIVE,
        ...     effect_strength=EffectStrength.STRONG,
        ...     confidence=0.88
        ... )
    """
    id: UUID = Field(default_factory=uuid4)
    ingredient_id: UUID
    effect_name: str = Field(..., min_length=1, max_length=255)
    effect_category: Optional[str] = Field(None, max_length=100)
    impact_direction: EffectDirection
    effect_strength: EffectStrength
    confidence: Optional[float] = Field(None, ge=0, le=1)
    dosage_dependent: bool = False
    mechanism: Optional[str] = None

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Round confidence to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        use_enum_values = True


class SymptomEffectModel(BaseTimestampedModel):
    """
    Model for symptom effects of ingredients.
    
    Represents effects on digestive symptoms and other health outcomes.
    
    Example:
        >>> effect = SymptomEffectModel(
        ...     ingredient_id=ingredient.id,
        ...     symptom_name="Bloating",
        ...     symptom_category="digestive",
        ...     effect_direction=EffectDirection.NEGATIVE,
        ...     effect_strength=EffectStrength.MODERATE,
        ...     confidence=0.70
        ... )
    """
    id: UUID = Field(default_factory=uuid4)
    ingredient_id: UUID
    symptom_name: str = Field(..., min_length=1, max_length=255)
    symptom_category: Optional[str] = Field(None, max_length=100)
    effect_direction: EffectDirection
    effect_strength: EffectStrength
    confidence: Optional[float] = Field(None, ge=0, le=1)
    dosage_dependent: bool = False
    population_notes: Optional[str] = None

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Round confidence to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        use_enum_values = True


class CitationModel(BaseTimestampedModel):
    """
    Model for scientific citations supporting ingredient effects.
    
    Represents scientific studies and publications with validation for PMID format.
    
    Example:
        >>> citation = CitationModel(
        ...     pmid="12345678",
        ...     title="Effects of probiotics on gut health",
        ...     authors="Smith J, Johnson A",
        ...     journal="Gut Health Research",
        ...     publication_year=2023,
        ...     study_type=StudyType.RCT,
        ...     sample_size=150,
        ...     study_quality=0.85
        ... )
    """
    id: UUID = Field(default_factory=uuid4)
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
        """Validate PMID format (1-8 digits)."""
        if v is not None:
            if not re.match(r'^\d{1,8}$', v):
                raise ValueError('PMID must be 1-8 digits')
        return v

    @field_validator('doi')
    @classmethod
    def validate_doi(cls, v):
        """Validate DOI format."""
        if v is not None:
            if not re.match(r'^10\.\d{4,}/.+', v):
                raise ValueError('DOI must start with "10." followed by registrant code and suffix')
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


class IngredientInteractionModel(BaseTimestampedModel):
    """
    Model for ingredient interactions and synergies.
    
    Represents how ingredients interact with each other (synergistic, antagonistic, etc.).
    
    Example:
        >>> interaction = IngredientInteractionModel(
        ...     ingredient_1_id=ingredient1.id,
        ...     ingredient_2_id=ingredient2.id,
        ...     interaction_type=InteractionType.SYNERGISTIC,
        ...     effect_description="Enhanced probiotic survival",
        ...     confidence=0.75
        ... )
    """
    id: UUID = Field(default_factory=uuid4)
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

    @model_validator(mode='after')
    def validate_different_ingredients(self):
        """Ensure ingredients are different and ordered correctly."""
        ing1_id = self.ingredient_1_id
        ing2_id = self.ingredient_2_id
        
        if ing1_id and ing2_id:
            if ing1_id == ing2_id:
                raise ValueError('Ingredients cannot interact with themselves')
            
            # Ensure consistent ordering (ingredient_1_id < ingredient_2_id)
            if ing1_id > ing2_id:
                self.ingredient_1_id = ing2_id
                self.ingredient_2_id = ing1_id
        
        return self

    class Config:
        use_enum_values = True


class CompleteIngredientModel(BaseModel):
    """
    Composite model combining ingredient with all its effects and citations.
    
    Provides a complete view of an ingredient including all associated data.
    
    Example:
        >>> complete_ingredient = CompleteIngredientModel(
        ...     ingredient=ingredient,
        ...     microbiome_effects=[microbiome_effect],
        ...     metabolic_effects=[metabolic_effect],
        ...     symptom_effects=[symptom_effect],
        ...     citations=[citation],
        ...     interactions=[interaction]
        ... )
    """
    ingredient: IngredientModel
    microbiome_effects: List[MicrobiomeEffectModel] = Field(default_factory=list)
    metabolic_effects: List[MetabolicEffectModel] = Field(default_factory=list)
    symptom_effects: List[SymptomEffectModel] = Field(default_factory=list)
    citations: List[CitationModel] = Field(default_factory=list)
    interactions: List[IngredientInteractionModel] = Field(default_factory=list)

    @property
    def total_effects_count(self) -> int:
        """Calculate total number of effects."""
        return (
            len(self.microbiome_effects) +
            len(self.metabolic_effects) +
            len(self.symptom_effects)
        )

    @property
    def average_confidence(self) -> float:
        """Calculate average confidence across all effects."""
        confidences = []
        
        for effect in self.microbiome_effects:
            if effect.confidence is not None:
                confidences.append(effect.confidence)
        
        for effect in self.metabolic_effects:
            if effect.confidence is not None:
                confidences.append(effect.confidence)
        
        for effect in self.symptom_effects:
            if effect.confidence is not None:
                confidences.append(effect.confidence)
        
        return round(sum(confidences) / len(confidences), 2) if confidences else 0.0

    class Config:
        use_enum_values = True


class IngredientCreateModel(BaseModel):
    """
    Model for creating new ingredients via API.
    
    Simplified model for ingredient creation without auto-generated fields.
    
    Example:
        >>> create_data = IngredientCreateModel(
        ...     name="New Probiotic Strain",
        ...     slug="new-probiotic-strain",
        ...     category=IngredientCategory.PROBIOTIC,
        ...     description="A novel probiotic strain",
        ...     gut_score=7.5,
        ...     confidence_score=0.65
        ... )
    """
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    aliases: List[str] = Field(default_factory=list)
    category: IngredientCategory
    description: Optional[str] = None
    gut_score: Optional[float] = Field(None, ge=0, le=10)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    dosage_info: Optional[Dict[str, Any]] = None
    safety_notes: Optional[str] = None

    @field_validator('gut_score')
    @classmethod
    def validate_gut_score(cls, v):
        """Validate gut score is between 0 and 10 with one decimal place."""
        if v is not None:
            return round(v, 1)
        return v

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        """Validate confidence score is between 0 and 1 with two decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format (lowercase, hyphens, alphanumeric)."""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('slug must contain only lowercase letters, numbers, and hyphens')
        return v

    class Config:
        use_enum_values = True


class IngredientResponseModel(BaseModel):
    """
    Model for API responses containing ingredient data.
    
    Optimized for API responses with computed fields and clean structure.
    
    Example:
        >>> response = IngredientResponseModel(
        ...     id=ingredient.id,
        ...     name=ingredient.name,
        ...     slug=ingredient.slug,
        ...     category=ingredient.category,
        ...     gut_score=ingredient.gut_score,
        ...     confidence_score=ingredient.confidence_score,
        ...     effects_count=5,
        ...     citations_count=3,
        ...     last_updated=ingredient.updated_at
        ... )
    """
    id: UUID
    name: str
    slug: str
    category: IngredientCategory
    description: Optional[str] = None
    gut_score: Optional[float] = None
    confidence_score: Optional[float] = None
    dosage_info: Optional[Dict[str, Any]] = None
    safety_notes: Optional[str] = None
    effects_count: int = 0
    citations_count: int = 0
    last_updated: datetime

    class Config:
        use_enum_values = True