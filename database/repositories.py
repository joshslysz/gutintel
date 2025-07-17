"""
Comprehensive database operations module for GutIntel using asyncpg and Pydantic models.

This module provides repository classes for database operations with transaction management,
query optimization, caching, and comprehensive error handling.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

import asyncpg
from asyncpg.exceptions import PostgresError, UniqueViolationError, ForeignKeyViolationError

from .connection import Database, get_database
from models.ingredient import (
    CompleteIngredientModel,
    IngredientModel,
    IngredientCreateModel,
    MicrobiomeEffectModel,
    MetabolicEffectModel,
    SymptomEffectModel,
    CitationModel,
    IngredientInteractionModel,
    IngredientCategory,
    EffectDirection,
    EffectStrength,
    BacteriaLevel,
    InteractionType,
    StudyType
)

logger = logging.getLogger(__name__)

# Type variables for generic repository
ModelType = TypeVar('ModelType')
CreateModelType = TypeVar('CreateModelType')


def _get_enum_value(enum_value: Union[str, Any]) -> str:
    """
    Helper function to extract string value from enum or return string as-is.
    
    Handles both actual enum objects and string values that may have been
    serialized by Pydantic's use_enum_values=True configuration.
    
    Args:
        enum_value: Either an enum object with .value attribute or a string
        
    Returns:
        String value suitable for database insertion
    """
    if isinstance(enum_value, str):
        return enum_value
    elif hasattr(enum_value, 'value'):
        return enum_value.value
    else:
        return str(enum_value)


class RepositoryError(Exception):
    """Base exception for repository operations."""
    pass


class IngredientNotFoundError(RepositoryError):
    """Raised when an ingredient is not found."""
    pass


class DuplicateIngredientError(RepositoryError):
    """Raised when attempting to create a duplicate ingredient."""
    pass


class ValidationError(RepositoryError):
    """Raised when validation fails."""
    pass


class DatabaseOperationError(RepositoryError):
    """Raised when database operation fails."""
    pass


class CacheManager:
    """Simple in-memory cache manager for frequently accessed data."""
    
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires_at']:
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL."""
        self.cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()


class BaseRepository(ABC):
    """
    Base repository class with common functionality.
    
    Provides transaction management, caching, and common database operations
    that can be extended by specific repository implementations.
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.cache = CacheManager()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @asynccontextmanager
    async def transaction(self):
        """
        Async context manager for database transactions.
        
        Automatically handles rollback on exceptions and provides
        proper error handling for transaction management.
        
        Example:
            async with repo.transaction() as conn:
                await conn.execute("INSERT INTO ...")
                await conn.execute("UPDATE ...")
                # Automatic commit on success, rollback on exception
        """
        try:
            async with self.db.transaction() as conn:
                yield conn
        except PostgresError as e:
            self.logger.error(f"Database transaction failed: {e}")
            raise DatabaseOperationError(f"Transaction failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in transaction: {e}")
            raise RepositoryError(f"Transaction error: {e}")
    
    def _build_cache_key(self, prefix: str, **kwargs) -> str:
        """Build cache key from prefix and keyword arguments."""
        key_parts = [prefix]
        for key, value in sorted(kwargs.items()):
            if value is not None:
                key_parts.append(f"{key}:{value}")
        return ":".join(key_parts)
    
    def _record_to_dict(self, record: asyncpg.Record) -> Dict[str, Any]:
        """Convert asyncpg Record to dictionary."""
        if record is None:
            return {}
        
        result = dict(record)
        
        # Parse JSON string fields that should be dictionaries
        json_fields = ['dosage_info', 'nutritional_info', 'interaction_info']
        for field in json_fields:
            if field in result and isinstance(result[field], str):
                try:
                    result[field] = json.loads(result[field])
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, keep as string or set to None
                    self.logger.warning(f"Failed to parse JSON field '{field}': {result[field]}")
                    result[field] = None
        
        return result
    
    def _validate_uuid(self, uuid_str: Union[str, UUID]) -> UUID:
        """Validate and convert UUID string to UUID object."""
        if isinstance(uuid_str, UUID):
            return uuid_str
        try:
            return UUID(str(uuid_str))
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid UUID format: {uuid_str}")
    
    async def _execute_with_retry(self, query: str, *args, max_retries: int = 3) -> Any:
        """Execute query with retry logic for transient failures."""
        for attempt in range(max_retries):
            try:
                return await self.db.execute(query, *args)
            except PostgresError as e:
                if attempt == max_retries - 1:
                    raise DatabaseOperationError(f"Query failed after {max_retries} attempts: {e}")
                await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
    
    async def _fetch_with_retry(self, query: str, *args, max_retries: int = 3) -> List[asyncpg.Record]:
        """Fetch query results with retry logic."""
        for attempt in range(max_retries):
            try:
                return await self.db.fetch(query, *args)
            except PostgresError as e:
                if attempt == max_retries - 1:
                    raise DatabaseOperationError(f"Fetch failed after {max_retries} attempts: {e}")
                await asyncio.sleep(0.5 * (2 ** attempt))


class IngredientRepository(BaseRepository):
    """
    Repository for ingredient database operations.
    
    Provides comprehensive CRUD operations, advanced queries, and data management
    for ingredients and their related effects, citations, and interactions.
    """
    
    async def create_ingredient(self, ingredient_data: CompleteIngredientModel) -> UUID:
        """
        Create a new ingredient with all its related data.
        
        Args:
            ingredient_data: Complete ingredient model with all effects and citations
            
        Returns:
            UUID: The ID of the created ingredient
            
        Raises:
            DuplicateIngredientError: If ingredient name or slug already exists
            ValidationError: If ingredient data is invalid
            DatabaseOperationError: If database operation fails
            
        Example:
            >>> ingredient = CompleteIngredientModel(
            ...     ingredient=IngredientModel(
            ...         name="Lactobacillus rhamnosus",
            ...         slug="lactobacillus-rhamnosus",
            ...         category=IngredientCategory.PROBIOTIC,
            ...         gut_score=8.5,
            ...         confidence_score=0.85
            ...     ),
            ...     microbiome_effects=[...],
            ...     metabolic_effects=[...]
            ... )
            >>> ingredient_id = await repo.create_ingredient(ingredient)
        """
        try:
            async with self.transaction() as conn:
                # Insert main ingredient
                ingredient_id = await self._insert_ingredient(conn, ingredient_data.ingredient)
                
                # Insert related effects
                await self._insert_microbiome_effects(conn, ingredient_id, ingredient_data.microbiome_effects)
                await self._insert_metabolic_effects(conn, ingredient_id, ingredient_data.metabolic_effects)
                await self._insert_symptom_effects(conn, ingredient_id, ingredient_data.symptom_effects)
                
                # Insert citations and links
                await self._insert_citations_and_links(conn, ingredient_id, ingredient_data.citations)
                
                # Insert interactions
                await self._insert_interactions(conn, ingredient_data.interactions)
                
                # Clear related caches
                self.cache.clear()
                
                self.logger.info(f"Created ingredient with ID: {ingredient_id}")
                return ingredient_id
                
        except UniqueViolationError as e:
            if 'ingredients_name_key' in str(e):
                raise DuplicateIngredientError(f"Ingredient name '{ingredient_data.ingredient.name}' already exists")
            elif 'ingredients_slug_key' in str(e):
                raise DuplicateIngredientError(f"Ingredient slug '{ingredient_data.ingredient.slug}' already exists")
            else:
                raise DatabaseOperationError(f"Unique constraint violation: {e}")
        except Exception as e:
            raise DatabaseOperationError(f"Failed to create ingredient: {e}")
    
    async def get_ingredient_by_id(self, ingredient_id: UUID) -> Optional[CompleteIngredientModel]:
        """
        Get ingredient by ID with all related data.
        
        Args:
            ingredient_id: UUID of the ingredient
            
        Returns:
            CompleteIngredientModel or None if not found
            
        Example:
            >>> ingredient = await repo.get_ingredient_by_id(ingredient_id)
            >>> if ingredient:
            ...     print(f"Gut score: {ingredient.ingredient.gut_score}")
        """
        ingredient_id = self._validate_uuid(ingredient_id)
        cache_key = self._build_cache_key("ingredient", id=str(ingredient_id))
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # Fetch ingredient data
            ingredient_record = await self.db.fetchrow(
                "SELECT * FROM ingredients WHERE id = $1", ingredient_id
            )
            
            if not ingredient_record:
                return None
            
            # Build complete ingredient model
            ingredient = await self._build_complete_ingredient(ingredient_record)
            
            # Cache the result
            self.cache.set(cache_key, ingredient)
            
            return ingredient
            
        except Exception as e:
            self.logger.error(f"Failed to get ingredient {ingredient_id}: {e}")
            raise DatabaseOperationError(f"Failed to get ingredient: {e}")
    
    async def get_ingredient_by_name(self, name: str) -> Optional[CompleteIngredientModel]:
        """
        Get ingredient by name with all related data.
        
        Args:
            name: Name of the ingredient
            
        Returns:
            CompleteIngredientModel or None if not found
        """
        if not name or not name.strip():
            raise ValidationError("Ingredient name cannot be empty")
        
        cache_key = self._build_cache_key("ingredient", name=name.lower())
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # Search by name (case-insensitive)
            ingredient_record = await self.db.fetchrow(
                "SELECT * FROM ingredients WHERE LOWER(name) = LOWER($1)", name
            )
            
            if not ingredient_record:
                return None
            
            # Build complete ingredient model
            ingredient = await self._build_complete_ingredient(ingredient_record)
            
            # Cache the result
            self.cache.set(cache_key, ingredient)
            
            return ingredient
            
        except Exception as e:
            self.logger.error(f"Failed to get ingredient by name '{name}': {e}")
            raise DatabaseOperationError(f"Failed to get ingredient by name: {e}")
    
    async def search_ingredients(
        self, 
        category: Optional[str] = None,
        min_gut_score: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IngredientModel]:
        """
        Search ingredients with optional filters.
        
        Args:
            category: Filter by ingredient category
            min_gut_score: Minimum gut score threshold
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of IngredientModel objects
            
        Example:
            >>> probiotics = await repo.search_ingredients(
            ...     category="probiotic",
            ...     min_gut_score=7.0
            ... )
        """
        cache_key = self._build_cache_key(
            "search", category=category, min_gut_score=min_gut_score, 
            limit=limit, offset=offset
        )
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # Build dynamic query
            conditions = []
            params = []
            param_count = 0
            
            if category:
                param_count += 1
                conditions.append(f"category = ${param_count}")
                params.append(category)
            
            if min_gut_score is not None:
                param_count += 1
                conditions.append(f"gut_score >= ${param_count}")
                params.append(min_gut_score)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            param_count += 1
            limit_clause = f"LIMIT ${param_count}"
            params.append(limit)
            
            param_count += 1
            offset_clause = f"OFFSET ${param_count}"
            params.append(offset)
            
            query = f"""
                SELECT * FROM ingredients 
                WHERE {where_clause}
                ORDER BY gut_score DESC NULLS LAST, name ASC
                {limit_clause} {offset_clause}
            """
            
            records = await self._fetch_with_retry(query, *params)
            
            # Convert to IngredientModel objects
            ingredients = []
            for record in records:
                ingredient_dict = self._record_to_dict(record)
                ingredients.append(IngredientModel(**ingredient_dict))
            
            # Cache the result
            self.cache.set(cache_key, ingredients)
            
            return ingredients
            
        except Exception as e:
            self.logger.error(f"Failed to search ingredients: {e}")
            raise DatabaseOperationError(f"Failed to search ingredients: {e}")
    
    async def update_ingredient(self, ingredient_id: UUID, updates: Dict[str, Any]) -> bool:
        """
        Update ingredient with provided fields.
        
        Args:
            ingredient_id: UUID of the ingredient to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if update successful, False if ingredient not found
            
        Example:
            >>> success = await repo.update_ingredient(
            ...     ingredient_id,
            ...     {"gut_score": 9.0, "confidence_score": 0.95}
            ... )
        """
        ingredient_id = self._validate_uuid(ingredient_id)
        
        if not updates:
            raise ValidationError("No updates provided")
        
        # Validate update fields
        allowed_fields = {
            'name', 'slug', 'aliases', 'category', 'description',
            'gut_score', 'confidence_score', 'dosage_info', 'safety_notes'
        }
        
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValidationError(f"Invalid update fields: {invalid_fields}")
        
        try:
            async with self.transaction() as conn:
                # Build dynamic update query
                set_clauses = []
                params = []
                param_count = 0
                
                for field, value in updates.items():
                    param_count += 1
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(value)
                
                param_count += 1
                params.append(ingredient_id)
                
                query = f"""
                    UPDATE ingredients 
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ${param_count}
                    RETURNING id
                """
                
                result = await conn.fetchrow(query, *params)
                
                if result:
                    # Clear related caches
                    self._clear_ingredient_caches(ingredient_id)
                    self.logger.info(f"Updated ingredient {ingredient_id}")
                    return True
                else:
                    return False
                    
        except UniqueViolationError as e:
            if 'ingredients_name_key' in str(e):
                raise DuplicateIngredientError(f"Ingredient name '{updates.get('name')}' already exists")
            elif 'ingredients_slug_key' in str(e):
                raise DuplicateIngredientError(f"Ingredient slug '{updates.get('slug')}' already exists")
            else:
                raise DatabaseOperationError(f"Unique constraint violation: {e}")
        except Exception as e:
            self.logger.error(f"Failed to update ingredient {ingredient_id}: {e}")
            raise DatabaseOperationError(f"Failed to update ingredient: {e}")
    
    async def delete_ingredient(self, ingredient_id: UUID) -> bool:
        """
        Delete ingredient and all related data.
        
        Args:
            ingredient_id: UUID of the ingredient to delete
            
        Returns:
            bool: True if deletion successful, False if ingredient not found
            
        Note:
            This will cascade delete all related effects, citations, and interactions
            due to foreign key constraints in the database schema.
        """
        ingredient_id = self._validate_uuid(ingredient_id)
        
        try:
            async with self.transaction() as conn:
                result = await conn.execute(
                    "DELETE FROM ingredients WHERE id = $1", ingredient_id
                )
                
                deleted = result.split()[-1] == '1'  # Extract affected row count
                
                if deleted:
                    # Clear related caches
                    self._clear_ingredient_caches(ingredient_id)
                    self.logger.info(f"Deleted ingredient {ingredient_id}")
                
                return deleted
                
        except ForeignKeyViolationError as e:
            raise DatabaseOperationError(f"Cannot delete ingredient due to foreign key constraint: {e}")
        except Exception as e:
            self.logger.error(f"Failed to delete ingredient {ingredient_id}: {e}")
            raise DatabaseOperationError(f"Failed to delete ingredient: {e}")
    
    async def get_ingredients_with_effects(self) -> List[CompleteIngredientModel]:
        """
        Get all ingredients that have at least one effect.
        
        Returns:
            List of CompleteIngredientModel objects with effects
        """
        cache_key = "ingredients_with_effects"
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            query = """
                SELECT DISTINCT i.* FROM ingredients i
                WHERE EXISTS (
                    SELECT 1 FROM microbiome_effects me WHERE me.ingredient_id = i.id
                    UNION
                    SELECT 1 FROM metabolic_effects met WHERE met.ingredient_id = i.id
                    UNION
                    SELECT 1 FROM symptom_effects se WHERE se.ingredient_id = i.id
                )
                ORDER BY i.gut_score DESC NULLS LAST, i.name ASC
            """
            
            records = await self._fetch_with_retry(query)
            
            # Build complete ingredient models
            ingredients = []
            for record in records:
                ingredient = await self._build_complete_ingredient(record)
                ingredients.append(ingredient)
            
            # Cache the result
            self.cache.set(cache_key, ingredients)
            
            return ingredients
            
        except Exception as e:
            self.logger.error(f"Failed to get ingredients with effects: {e}")
            raise DatabaseOperationError(f"Failed to get ingredients with effects: {e}")
    
    async def search_by_bacteria(self, bacteria_name: str) -> List[IngredientModel]:
        """
        Search ingredients by bacteria name they affect.
        
        Args:
            bacteria_name: Name of the bacteria to search for
            
        Returns:
            List of IngredientModel objects
            
        Example:
            >>> ingredients = await repo.search_by_bacteria("Lactobacillus")
        """
        if not bacteria_name or not bacteria_name.strip():
            raise ValidationError("Bacteria name cannot be empty")
        
        cache_key = self._build_cache_key("bacteria_search", bacteria=bacteria_name.lower())
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            query = """
                SELECT DISTINCT i.* FROM ingredients i
                JOIN microbiome_effects me ON i.id = me.ingredient_id
                WHERE LOWER(me.bacteria_name) LIKE LOWER($1)
                ORDER BY i.gut_score DESC NULLS LAST, i.name ASC
            """
            
            records = await self._fetch_with_retry(query, f"%{bacteria_name}%")
            
            # Convert to IngredientModel objects
            ingredients = []
            for record in records:
                ingredient_dict = self._record_to_dict(record)
                ingredients.append(IngredientModel(**ingredient_dict))
            
            # Cache the result
            self.cache.set(cache_key, ingredients)
            
            return ingredients
            
        except Exception as e:
            self.logger.error(f"Failed to search by bacteria '{bacteria_name}': {e}")
            raise DatabaseOperationError(f"Failed to search by bacteria: {e}")
    
    async def get_high_confidence_ingredients(self, min_confidence: float = 0.8) -> List[IngredientModel]:
        """
        Get ingredients with high confidence scores.
        
        Args:
            min_confidence: Minimum confidence score (default: 0.8)
            
        Returns:
            List of IngredientModel objects with high confidence
        """
        if not (0 <= min_confidence <= 1):
            raise ValidationError("Confidence must be between 0 and 1")
        
        cache_key = self._build_cache_key("high_confidence", min_confidence=min_confidence)
        
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            query = """
                SELECT * FROM ingredients 
                WHERE confidence_score >= $1
                ORDER BY confidence_score DESC, gut_score DESC NULLS LAST, name ASC
            """
            
            records = await self._fetch_with_retry(query, min_confidence)
            
            # Convert to IngredientModel objects
            ingredients = []
            for record in records:
                ingredient_dict = self._record_to_dict(record)
                ingredients.append(IngredientModel(**ingredient_dict))
            
            # Cache the result
            self.cache.set(cache_key, ingredients)
            
            return ingredients
            
        except Exception as e:
            self.logger.error(f"Failed to get high confidence ingredients: {e}")
            raise DatabaseOperationError(f"Failed to get high confidence ingredients: {e}")
    
    async def bulk_create_ingredients(self, ingredients: List[CompleteIngredientModel]) -> List[UUID]:
        """
        Create multiple ingredients in a single transaction.
        
        Args:
            ingredients: List of CompleteIngredientModel objects to create
            
        Returns:
            List of UUIDs for created ingredients
            
        Raises:
            ValidationError: If any ingredient data is invalid
            DatabaseOperationError: If bulk creation fails
            
        Example:
            >>> ingredient_ids = await repo.bulk_create_ingredients([
            ...     ingredient1, ingredient2, ingredient3
            ... ])
        """
        if not ingredients:
            raise ValidationError("No ingredients provided for bulk creation")
        
        try:
            created_ids = []
            
            async with self.transaction() as conn:
                for ingredient_data in ingredients:
                    # Insert main ingredient
                    ingredient_id = await self._insert_ingredient(conn, ingredient_data.ingredient)
                    created_ids.append(ingredient_id)
                    
                    # Insert related effects
                    await self._insert_microbiome_effects(conn, ingredient_id, ingredient_data.microbiome_effects)
                    await self._insert_metabolic_effects(conn, ingredient_id, ingredient_data.metabolic_effects)
                    await self._insert_symptom_effects(conn, ingredient_id, ingredient_data.symptom_effects)
                    
                    # Insert citations and links
                    await self._insert_citations_and_links(conn, ingredient_id, ingredient_data.citations)
                    
                    # Insert interactions
                    await self._insert_interactions(conn, ingredient_data.interactions)
                
                # Clear caches after bulk operation
                self.cache.clear()
                
                self.logger.info(f"Bulk created {len(created_ids)} ingredients")
                return created_ids
                
        except Exception as e:
            self.logger.error(f"Failed to bulk create ingredients: {e}")
            raise DatabaseOperationError(f"Failed to bulk create ingredients: {e}")
    
    # Private helper methods
    
    async def _insert_ingredient(self, conn: asyncpg.Connection, ingredient: IngredientModel) -> UUID:
        """Insert ingredient into database."""
        query = """
            INSERT INTO ingredients (id, name, slug, aliases, category, description, 
                                   gut_score, confidence_score, dosage_info, safety_notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
        """
        
        return await conn.fetchval(
            query,
            ingredient.id,
            ingredient.name,
            ingredient.slug,
            ingredient.aliases,
            _get_enum_value(ingredient.category),
            ingredient.description,
            ingredient.gut_score,
            ingredient.confidence_score,
            json.dumps(ingredient.dosage_info) if ingredient.dosage_info else None,
            ingredient.safety_notes
        )
    
    async def _insert_microbiome_effects(
        self, 
        conn: asyncpg.Connection, 
        ingredient_id: UUID, 
        effects: List[MicrobiomeEffectModel]
    ) -> None:
        """Insert microbiome effects for an ingredient."""
        if not effects:
            return
        
        query = """
            INSERT INTO microbiome_effects (id, ingredient_id, bacteria_name, bacteria_level,
                                          effect_type, effect_strength, confidence, mechanism)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        
        for effect in effects:
            await conn.execute(
                query,
                effect.id,
                ingredient_id,
                effect.bacteria_name,
                _get_enum_value(effect.bacteria_level),
                effect.effect_type,
                _get_enum_value(effect.effect_strength),
                effect.confidence,
                effect.mechanism
            )
    
    async def _insert_metabolic_effects(
        self, 
        conn: asyncpg.Connection, 
        ingredient_id: UUID, 
        effects: List[MetabolicEffectModel]
    ) -> None:
        """Insert metabolic effects for an ingredient."""
        if not effects:
            return
        
        query = """
            INSERT INTO metabolic_effects (id, ingredient_id, effect_name, effect_category,
                                         impact_direction, effect_strength, confidence, 
                                         dosage_dependent, mechanism)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        for effect in effects:
            await conn.execute(
                query,
                effect.id,
                ingredient_id,
                effect.effect_name,
                effect.effect_category,
                _get_enum_value(effect.impact_direction),
                _get_enum_value(effect.effect_strength),
                effect.confidence,
                effect.dosage_dependent,
                effect.mechanism
            )
    
    async def _insert_symptom_effects(
        self, 
        conn: asyncpg.Connection, 
        ingredient_id: UUID, 
        effects: List[SymptomEffectModel]
    ) -> None:
        """Insert symptom effects for an ingredient."""
        if not effects:
            return
        
        query = """
            INSERT INTO symptom_effects (id, ingredient_id, symptom_name, symptom_category,
                                       effect_direction, effect_strength, confidence, 
                                       dosage_dependent, population_notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        for effect in effects:
            await conn.execute(
                query,
                effect.id,
                ingredient_id,
                effect.symptom_name,
                effect.symptom_category,
                _get_enum_value(effect.effect_direction),
                _get_enum_value(effect.effect_strength),
                effect.confidence,
                effect.dosage_dependent,
                effect.population_notes
            )
    
    async def _insert_citations_and_links(
        self, 
        conn: asyncpg.Connection, 
        ingredient_id: UUID, 
        citations: List[CitationModel]
    ) -> None:
        """Insert citations and their links to effects."""
        if not citations:
            return
        
        citation_query = """
            INSERT INTO citations (id, pmid, doi, title, authors, journal, 
                                 publication_year, study_type, sample_size, study_quality)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (pmid) DO UPDATE SET
                title = EXCLUDED.title,
                authors = EXCLUDED.authors,
                journal = EXCLUDED.journal,
                publication_year = EXCLUDED.publication_year,
                study_type = EXCLUDED.study_type,
                sample_size = EXCLUDED.sample_size,
                study_quality = EXCLUDED.study_quality,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        
        for citation in citations:
            await conn.execute(
                citation_query,
                citation.id,
                citation.pmid,
                citation.doi,
                citation.title,
                citation.authors,
                citation.journal,
                citation.publication_year,
                _get_enum_value(citation.study_type),
                citation.sample_size,
                citation.study_quality
            )
    
    async def _insert_interactions(
        self, 
        conn: asyncpg.Connection, 
        interactions: List[IngredientInteractionModel]
    ) -> None:
        """Insert ingredient interactions."""
        if not interactions:
            return
        
        query = """
            INSERT INTO ingredient_interactions (id, ingredient_1_id, ingredient_2_id,
                                               interaction_type, effect_description, confidence)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (ingredient_1_id, ingredient_2_id) DO UPDATE SET
                interaction_type = EXCLUDED.interaction_type,
                effect_description = EXCLUDED.effect_description,
                confidence = EXCLUDED.confidence,
                updated_at = CURRENT_TIMESTAMP
        """
        
        for interaction in interactions:
            await conn.execute(
                query,
                interaction.id,
                interaction.ingredient_1_id,
                interaction.ingredient_2_id,
                _get_enum_value(interaction.interaction_type),
                interaction.effect_description,
                interaction.confidence
            )
    
    async def _build_complete_ingredient(self, ingredient_record: asyncpg.Record) -> CompleteIngredientModel:
        """Build complete ingredient model from database record."""
        ingredient_dict = self._record_to_dict(ingredient_record)
        
        # Parse JSON fields
        if ingredient_dict.get('dosage_info'):
            ingredient_dict['dosage_info'] = json.loads(ingredient_dict['dosage_info'])
        
        ingredient = IngredientModel(**ingredient_dict)
        
        # Fetch related data
        microbiome_effects = await self._fetch_microbiome_effects(ingredient.id)
        metabolic_effects = await self._fetch_metabolic_effects(ingredient.id)
        symptom_effects = await self._fetch_symptom_effects(ingredient.id)
        citations = await self._fetch_citations(ingredient.id)
        interactions = await self._fetch_interactions(ingredient.id)
        
        return CompleteIngredientModel(
            ingredient=ingredient,
            microbiome_effects=microbiome_effects,
            metabolic_effects=metabolic_effects,
            symptom_effects=symptom_effects,
            citations=citations,
            interactions=interactions
        )
    
    async def _fetch_microbiome_effects(self, ingredient_id: UUID) -> List[MicrobiomeEffectModel]:
        """Fetch microbiome effects for an ingredient."""
        records = await self.db.fetch(
            "SELECT * FROM microbiome_effects WHERE ingredient_id = $1 ORDER BY bacteria_name",
            ingredient_id
        )
        
        effects = []
        for record in records:
            effect_dict = self._record_to_dict(record)
            effects.append(MicrobiomeEffectModel(**effect_dict))
        
        return effects
    
    async def _fetch_metabolic_effects(self, ingredient_id: UUID) -> List[MetabolicEffectModel]:
        """Fetch metabolic effects for an ingredient."""
        records = await self.db.fetch(
            "SELECT * FROM metabolic_effects WHERE ingredient_id = $1 ORDER BY effect_name",
            ingredient_id
        )
        
        effects = []
        for record in records:
            effect_dict = self._record_to_dict(record)
            effects.append(MetabolicEffectModel(**effect_dict))
        
        return effects
    
    async def _fetch_symptom_effects(self, ingredient_id: UUID) -> List[SymptomEffectModel]:
        """Fetch symptom effects for an ingredient."""
        records = await self.db.fetch(
            "SELECT * FROM symptom_effects WHERE ingredient_id = $1 ORDER BY symptom_name",
            ingredient_id
        )
        
        effects = []
        for record in records:
            effect_dict = self._record_to_dict(record)
            effects.append(SymptomEffectModel(**effect_dict))
        
        return effects
    
    async def _fetch_citations(self, ingredient_id: UUID) -> List[CitationModel]:
        """Fetch citations for an ingredient."""
        query = """
            SELECT DISTINCT c.* FROM citations c
            JOIN effect_citations ec ON c.id = ec.citation_id
            WHERE ec.effect_id IN (
                SELECT id FROM microbiome_effects WHERE ingredient_id = $1
                UNION
                SELECT id FROM metabolic_effects WHERE ingredient_id = $1
                UNION
                SELECT id FROM symptom_effects WHERE ingredient_id = $1
            )
            ORDER BY c.publication_year DESC, c.title
        """
        
        records = await self.db.fetch(query, ingredient_id)
        
        citations = []
        for record in records:
            citation_dict = self._record_to_dict(record)
            citations.append(CitationModel(**citation_dict))
        
        return citations
    
    async def _fetch_interactions(self, ingredient_id: UUID) -> List[IngredientInteractionModel]:
        """Fetch interactions for an ingredient."""
        records = await self.db.fetch(
            """
            SELECT * FROM ingredient_interactions 
            WHERE ingredient_1_id = $1 OR ingredient_2_id = $1
            ORDER BY interaction_type, effect_description
            """,
            ingredient_id
        )
        
        interactions = []
        for record in records:
            interaction_dict = self._record_to_dict(record)
            interactions.append(IngredientInteractionModel(**interaction_dict))
        
        return interactions
    
    def _clear_ingredient_caches(self, ingredient_id: UUID) -> None:
        """Clear all caches related to an ingredient."""
        # Clear specific ingredient caches
        self.cache.delete(f"ingredient:id:{ingredient_id}")
        
        # Clear general caches that might include this ingredient
        cache_patterns = [
            "search:", "ingredients_with_effects", "high_confidence:", "bacteria_search:"
        ]
        
        keys_to_delete = []
        for key in self.cache.cache.keys():
            if any(pattern in key for pattern in cache_patterns):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.cache.delete(key)


# Factory function to create repository instances
async def create_ingredient_repository(db: Optional[Database] = None) -> IngredientRepository:
    """
    Create an IngredientRepository instance.
    
    Args:
        db: Database instance (optional, will use global instance if not provided)
        
    Returns:
        IngredientRepository instance
        
    Example:
        >>> repo = await create_ingredient_repository()
        >>> ingredient = await repo.get_ingredient_by_name("Lactobacillus")
    """
    if db is None:
        db = await get_database()
    
    return IngredientRepository(db)