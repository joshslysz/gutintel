"""
Custom validators for GutIntel models.

This module provides additional validation utilities and custom validators
for complex validation scenarios across the application.
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from pydantic import field_validator, ValidationError


class ValidationUtils:
    """Utility class for common validation functions."""
    
    @staticmethod
    def validate_pmid(pmid: str) -> bool:
        """
        Validate PMID format.
        
        Args:
            pmid: PubMed ID string
            
        Returns:
            bool: True if valid PMID format
            
        Example:
            >>> ValidationUtils.validate_pmid("12345678")
            True
            >>> ValidationUtils.validate_pmid("invalid")
            False
        """
        if not pmid:
            return False
        return bool(re.match(r'^\d{1,8}$', pmid))
    
    @staticmethod
    def validate_doi(doi: str) -> bool:
        """
        Validate DOI format.
        
        Args:
            doi: Digital Object Identifier string
            
        Returns:
            bool: True if valid DOI format
            
        Example:
            >>> ValidationUtils.validate_doi("10.1234/example.doi")
            True
            >>> ValidationUtils.validate_doi("invalid-doi")
            False
        """
        if not doi:
            return False
        return bool(re.match(r'^10\.\d{4,}/.+', doi))
    
    @staticmethod
    def validate_slug(slug: str) -> bool:
        """
        Validate slug format (lowercase, hyphens, alphanumeric).
        
        Args:
            slug: URL-friendly slug string
            
        Returns:
            bool: True if valid slug format
            
        Example:
            >>> ValidationUtils.validate_slug("valid-slug-123")
            True
            >>> ValidationUtils.validate_slug("Invalid_Slug")
            False
        """
        if not slug:
            return False
        return bool(re.match(r'^[a-z0-9-]+$', slug))
    
    @staticmethod
    def validate_score_range(score: float, min_val: float, max_val: float) -> bool:
        """
        Validate score is within specified range.
        
        Args:
            score: Score to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            bool: True if score is within range
            
        Example:
            >>> ValidationUtils.validate_score_range(7.5, 0, 10)
            True
            >>> ValidationUtils.validate_score_range(15, 0, 10)
            False
        """
        return min_val <= score <= max_val
    
    @staticmethod
    def validate_dosage_info(dosage_info: Dict[str, Any]) -> bool:
        """
        Validate dosage information structure.
        
        Args:
            dosage_info: Dictionary containing dosage information
            
        Returns:
            bool: True if dosage info is valid
            
        Example:
            >>> ValidationUtils.validate_dosage_info({"min_dose": 100, "unit": "mg"})
            True
            >>> ValidationUtils.validate_dosage_info({"invalid_key": "value"})
            False
        """
        if not isinstance(dosage_info, dict):
            return False
        
        valid_keys = {
            'min_dose', 'max_dose', 'unit', 'frequency', 'duration',
            'min_cfu', 'max_cfu', 'form', 'timing', 'notes', 'concentration'
        }
        
        return all(key in valid_keys for key in dosage_info.keys())
    
    @staticmethod
    def validate_ingredient_name(name: str) -> bool:
        """
        Validate ingredient name format.
        
        Args:
            name: Ingredient name string
            
        Returns:
            bool: True if valid name format
            
        Example:
            >>> ValidationUtils.validate_ingredient_name("Lactobacillus acidophilus")
            True
            >>> ValidationUtils.validate_ingredient_name("")
            False
        """
        if not name or not name.strip():
            return False
        
        # Check for reasonable length
        if len(name) > 255:
            return False
        
        # Check for basic formatting (no leading/trailing whitespace)
        if name != name.strip():
            return False
        
        return True
    
    @staticmethod
    def validate_bacteria_name(bacteria_name: str) -> bool:
        """
        Validate bacterial name format.
        
        Args:
            bacteria_name: Scientific name of bacteria
            
        Returns:
            bool: True if valid bacteria name format
            
        Example:
            >>> ValidationUtils.validate_bacteria_name("Escherichia coli")
            True
            >>> ValidationUtils.validate_bacteria_name("invalid name")
            False
        """
        if not bacteria_name or not bacteria_name.strip():
            return False
        
        # Basic check for scientific name format (Genus species)
        parts = bacteria_name.split()
        if len(parts) < 2:
            return False
        
        # First part should be capitalized (Genus)
        if not parts[0][0].isupper():
            return False
        
        # Second part should be lowercase (species)
        if not parts[1][0].islower():
            return False
        
        return True
    
    @staticmethod
    def normalize_ingredient_list(ingredients: List[str]) -> List[str]:
        """
        Normalize a list of ingredients by removing duplicates and cleaning.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            List[str]: Cleaned and deduplicated ingredient list
            
        Example:
            >>> ValidationUtils.normalize_ingredient_list(["  Yogurt  ", "yogurt", "Banana"])
            ['Yogurt', 'Banana']
        """
        seen = set()
        normalized = []
        
        for ingredient in ingredients:
            # Clean and normalize
            cleaned = ingredient.strip()
            if not cleaned:
                continue
                
            # Check for duplicates (case-insensitive)
            lower_cleaned = cleaned.lower()
            if lower_cleaned not in seen:
                seen.add(lower_cleaned)
                normalized.append(cleaned)
        
        return normalized
    
    @staticmethod
    def validate_confidence_score(score: float) -> float:
        """
        Validate and normalize confidence score.
        
        Args:
            score: Confidence score (0-1)
            
        Returns:
            float: Normalized confidence score (rounded to 2 decimal places)
            
        Raises:
            ValueError: If score is not between 0 and 1
            
        Example:
            >>> ValidationUtils.validate_confidence_score(0.8543)
            0.85
        """
        if not 0 <= score <= 1:
            raise ValueError("Confidence score must be between 0 and 1")
        return round(score, 2)
    
    @staticmethod
    def validate_gut_score(score: float) -> float:
        """
        Validate and normalize gut score.
        
        Args:
            score: Gut score (0-10)
            
        Returns:
            float: Normalized gut score (rounded to 1 decimal place)
            
        Raises:
            ValueError: If score is not between 0 and 10
            
        Example:
            >>> ValidationUtils.validate_gut_score(7.89)
            7.9
        """
        if not 0 <= score <= 10:
            raise ValueError("Gut score must be between 0 and 10")
        return round(score, 1)


class CustomValidators:
    """Collection of custom Pydantic validators."""
    
    @staticmethod
    def pmid_validator(cls, v):
        """Pydantic validator for PMID field."""
        if v is not None and not ValidationUtils.validate_pmid(v):
            raise ValueError('PMID must be 1-8 digits')
        return v
    
    @staticmethod
    def doi_validator(cls, v):
        """Pydantic validator for DOI field."""
        if v is not None and not ValidationUtils.validate_doi(v):
            raise ValueError('DOI must start with "10." followed by registrant code and suffix')
        return v
    
    @staticmethod
    def slug_validator(cls, v):
        """Pydantic validator for slug field."""
        if not ValidationUtils.validate_slug(v):
            raise ValueError('slug must contain only lowercase letters, numbers, and hyphens')
        return v
    
    @staticmethod
    def ingredient_name_validator(cls, v):
        """Pydantic validator for ingredient name field."""
        if not ValidationUtils.validate_ingredient_name(v):
            raise ValueError('ingredient name must be non-empty and properly formatted')
        return v.strip()
    
    @staticmethod
    def bacteria_name_validator(cls, v):
        """Pydantic validator for bacteria name field."""
        if not ValidationUtils.validate_bacteria_name(v):
            raise ValueError('bacteria name must follow scientific naming format (Genus species)')
        return v
    
    @staticmethod
    def dosage_info_validator(cls, v):
        """Pydantic validator for dosage info field."""
        if v is not None and not ValidationUtils.validate_dosage_info(v):
            raise ValueError('dosage_info contains invalid keys')
        return v
    
    @staticmethod
    def confidence_score_validator(cls, v):
        """Pydantic validator for confidence score field."""
        if v is not None:
            return ValidationUtils.validate_confidence_score(v)
        return v
    
    @staticmethod
    def gut_score_validator(cls, v):
        """Pydantic validator for gut score field."""
        if v is not None:
            return ValidationUtils.validate_gut_score(v)
        return v
    
    @staticmethod
    def ingredient_list_validator(cls, v):
        """Pydantic validator for ingredient list field."""
        if v is not None:
            return ValidationUtils.normalize_ingredient_list(v)
        return v


class ValidationError(Exception):
    """Custom validation error for GutIntel models."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
    
    def __str__(self):
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class BatchValidator:
    """Validator for batch operations."""
    
    @staticmethod
    def validate_batch_size(items: List[Any], max_size: int = 100) -> bool:
        """
        Validate batch operation size.
        
        Args:
            items: List of items to validate
            max_size: Maximum allowed batch size
            
        Returns:
            bool: True if batch size is valid
            
        Raises:
            ValidationError: If batch size exceeds maximum
        """
        if len(items) > max_size:
            raise ValidationError(f"Batch size {len(items)} exceeds maximum of {max_size}")
        return True
    
    @staticmethod
    def validate_batch_operation(operation: str) -> bool:
        """
        Validate batch operation type.
        
        Args:
            operation: Operation type string
            
        Returns:
            bool: True if operation is valid
            
        Raises:
            ValidationError: If operation type is invalid
        """
        valid_operations = {'create', 'update', 'delete'}
        if operation not in valid_operations:
            raise ValidationError(f"Invalid operation '{operation}'. Must be one of: {valid_operations}")
        return True


class DataIntegrityValidator:
    """Validator for data integrity checks."""
    
    @staticmethod
    def validate_ingredient_effects_consistency(
        ingredient_id: str,
        effects: List[Dict[str, Any]]
    ) -> bool:
        """
        Validate that all effects belong to the same ingredient.
        
        Args:
            ingredient_id: The ingredient ID
            effects: List of effect dictionaries
            
        Returns:
            bool: True if all effects are consistent
            
        Raises:
            ValidationError: If effects don't match ingredient
        """
        for effect in effects:
            if effect.get('ingredient_id') != ingredient_id:
                raise ValidationError(
                    f"Effect ingredient_id {effect.get('ingredient_id')} doesn't match {ingredient_id}"
                )
        return True
    
    @staticmethod
    def validate_citation_pmid_uniqueness(
        citations: List[Dict[str, Any]]
    ) -> bool:
        """
        Validate that PMID values are unique across citations.
        
        Args:
            citations: List of citation dictionaries
            
        Returns:
            bool: True if all PMIDs are unique
            
        Raises:
            ValidationError: If duplicate PMIDs are found
        """
        pmids = []
        for citation in citations:
            pmid = citation.get('pmid')
            if pmid:
                if pmid in pmids:
                    raise ValidationError(f"Duplicate PMID found: {pmid}")
                pmids.append(pmid)
        return True
    
    @staticmethod
    def validate_interaction_ingredients(
        ingredient_1_id: str,
        ingredient_2_id: str
    ) -> bool:
        """
        Validate ingredient interaction constraints.
        
        Args:
            ingredient_1_id: First ingredient ID
            ingredient_2_id: Second ingredient ID
            
        Returns:
            bool: True if interaction is valid
            
        Raises:
            ValidationError: If ingredients are the same
        """
        if ingredient_1_id == ingredient_2_id:
            raise ValidationError("Ingredients cannot interact with themselves")
        return True