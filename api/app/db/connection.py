import json
import logging
import os
import asyncpg
from functools import wraps

logger = logging.getLogger(__name__)

# Module-level singleton for the connection pool
_pool: asyncpg.Pool | None = None

def _get_dsn() -> str:
    """Constructs the PostgreSQL connection string from environment variables."""
    user = os.getenv("POSTGRES_USER", "bough_user")
    password = os.getenv("POSTGRES_PASSWORD", "bough_pwd")
    db = os.getenv("POSTGRES_DB", "bough_db")
    host = os.getenv("POSTGRES_HOST", "db")
    return f"postgresql://{user}:{password}@{host}:5432/{db}"

async def _init_connection(conn: asyncpg.Connection) -> None:
    """
    Sets up custom codecs for every database connection created in the pool.
    This automatically translates Python dictionaries/lists to JSONB, and vice-versa.
    """
    try:
        # Register standard library json encoder/decoder for json and jsonb types
        await conn.set_type_codec(
            "jsonb",
            encoder=json.dumps,
            decoder=json.loads,
            schema="pg_catalog"
        )
        await conn.set_type_codec(
            "json",
            encoder=json.dumps,
            decoder=json.loads,
            schema="pg_catalog"
        )
        logger.debug("Database connection custom codecs successfully registered.")
    except Exception as e:
        logger.error("Failed to register custom codecs on database connection: %s", e)
        raise

async def init_pool() -> None:
    """Initializes the database connection pool with automatic connection initialization."""
    global _pool
    if _pool is not None:
        logger.warning("Database pool is already initialized.")
        return
    
    dsn = _get_dsn()
    try:
        logger.info("Initializing database connection pool...")
        _pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
            max_size=5,
            init=_init_connection  # Runs our codec setup for every connection
        )
        logger.info("Database connection pool initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database pool: %s", e)
        raise

async def close_pool() -> None:
    """Gracefully closes the database connection pool."""
    global _pool
    if _pool is None:
        logger.warning("Database pool is not initialized.")
        return
    
    logger.info("Closing database connection pool...")
    await _pool.close()
    _pool = None
    logger.info("Database connection pool closed.")

def get_pool() -> asyncpg.Pool:
    """Returns the current connection pool, raising if not initialized."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_pool() first.")
    return _pool

def with_connection(func):
    """Decorator that handles connection acquisition for DB functions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract conn from kwargs if present
        conn = kwargs.pop('conn', None)

        if conn:
            return await func(conn=conn, *args, **kwargs)
        
        pool = get_pool()
        async with pool.acquire() as conn:
            return await func(conn=conn, *args, **kwargs)
    return wrapper