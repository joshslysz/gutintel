"""
Database utilities and dependency injection for FastAPI.
"""
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import HTTPException, status
import sys
import os

# Add parent directory to path to access database modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.connection import Database
from database.repositories import IngredientRepository, create_ingredient_repository
from config import get_settings

# Global database instance
_db: Database = None

async def init_db():
    """Initialize database connection."""
    global _db
    settings = get_settings()
    _db = Database(database_url=settings.database_url)  # FIXED: removed asterisks
    await _db.connect()

async def close_db():
    """Close database connection."""
    global _db
    if _db:
        await _db.disconnect()

async def get_database():
    """FastAPI dependency for database connection."""
    global _db
    if _db is None:
        await init_db()
    yield _db

async def get_ingredient_repository():
    """FastAPI dependency for ingredient repository."""
    global _db
    if _db is None:
        await init_db()
    yield IngredientRepository(_db)

async def health_check() -> bool:
    """Check database health."""
    try:
        global _db
        if _db is None:
            await init_db()
        # Simple query to check connection
        result = await _db.fetchval("SELECT 1")
        return result == 1
    except Exception:
        return False
