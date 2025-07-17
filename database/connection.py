import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional, Any, Dict, List
import asyncpg
from asyncpg.exceptions import PostgresError


logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors"""
    pass


class Database:
    """Database connection manager with connection pooling and retry logic"""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        min_connections: int = 5,
        max_connections: int = 20,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        command_timeout: float = 30.0
    ):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL must be provided or set as environment variable")
        
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.command_timeout = command_timeout
        self.pool: Optional[asyncpg.Pool] = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """Establish database connection pool with retry logic"""
        if self._is_connected:
            return
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{self.max_retries})")
                
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=self.min_connections,
                    max_size=self.max_connections,
                    command_timeout=self.command_timeout,
                    statement_cache_size=0,
                    server_settings={
                        'jit': 'off',
                        'application_name': 'gutintel'
                    }
                )
                
                # Test the connection
                async with self.pool.acquire() as conn:
                    await conn.execute('SELECT 1')
                
                self._is_connected = True
                logger.info("Database connection pool established successfully")
                return
                
            except (PostgresError, OSError, asyncio.TimeoutError) as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise DatabaseConnectionError(f"Failed to connect to database after {self.max_retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during database connection: {e}")
                raise DatabaseConnectionError(f"Unexpected database connection error: {e}")
    
    async def disconnect(self) -> None:
        """Close database connection pool"""
        if self.pool and not self.pool._closed:
            await self.pool.close()
            self._is_connected = False
            logger.info("Database connection pool closed")
    
    async def test_connection(self) -> bool:
        """Test database connection and return connection status"""
        try:
            if not self.pool:
                await self.connect()
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchval('SELECT 1')
                return result == 1
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query that doesn't return rows"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            try:
                return await conn.execute(query, *args)
            except PostgresError as e:
                logger.error(f"Database query execution failed: {e}")
                raise DatabaseConnectionError(f"Query execution failed: {e}")
    
    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch multiple rows from a query"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            try:
                return await conn.fetch(query, *args)
            except PostgresError as e:
                logger.error(f"Database fetch failed: {e}")
                raise DatabaseConnectionError(f"Fetch failed: {e}")
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row from a query"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            try:
                return await conn.fetchrow(query, *args)
            except PostgresError as e:
                logger.error(f"Database fetchrow failed: {e}")
                raise DatabaseConnectionError(f"Fetchrow failed: {e}")
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value from a query"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            try:
                return await conn.fetchval(query, *args)
            except PostgresError as e:
                logger.error(f"Database fetchval failed: {e}")
                raise DatabaseConnectionError(f"Fetchval failed: {e}")
    
    @asynccontextmanager
    async def transaction(self):
        """Async context manager for database transactions"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn
    
    @asynccontextmanager
    async def connection(self):
        """Async context manager for database connections"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected and self.pool and not self.pool._closed


# Global database instance
db = None


async def get_database() -> Database:
    """Get the global database instance"""
    return db


async def init_database(database_url: Optional[str] = None) -> Database:
    """Initialize database connection"""
    global db
    if database_url:
        db = Database(database_url)
    await db.connect()
    return db


async def close_database() -> None:
    """Close database connection"""
    global db
    if db:
        await db.disconnect()