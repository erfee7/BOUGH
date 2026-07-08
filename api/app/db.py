import logging
import os
import uuid
import asyncpg

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

async def init_pool() -> None:
    """Initializes the database connection pool."""
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

# --- Basic Query Functions ---

async def create_conversation(title: str | None, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """
    Creates a new conversation in the database.
    If conn is provided, uses it; otherwise, acquires a connection from the pool.
    """
    if conn:
        return await _create_conversation(conn, title)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _create_conversation(conn, title)

async def _create_conversation(conn: asyncpg.Connection, title: str | None) -> uuid.UUID:
    query = "INSERT INTO conversations (title) VALUES ($1) RETURNING id;"
    row = await conn.fetchrow(query, title)
    logger.info("Created new conversation with ID: %s", row['id'])
    return row['id']

async def fetch_conversation(conv_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> asyncpg.Record | None:
    """
    Fetches a single conversation by its ID.
    """
    if conn:
        return await _fetch_conversation(conn, conv_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _fetch_conversation(conn, conv_id)

async def _fetch_conversation(conn: asyncpg.Connection, conv_id: uuid.UUID) -> asyncpg.Record | None:
    query = "SELECT id, title, created_at FROM conversations WHERE id = $1;"
    return await conn.fetchrow(query, conv_id)