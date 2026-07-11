import logging
import uuid
import asyncpg
from app.db.connection import get_pool

logger = logging.getLogger(__name__)

async def create_conversation(title: str | None, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """Creates a new conversation in the database."""
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

async def fetch_conversation(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> asyncpg.Record | None:
    """Fetches a single conversation by its ID."""
    if conn:
        return await _fetch_conversation(conn, conversation_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _fetch_conversation(conn, conversation_id)

async def _fetch_conversation(conn: asyncpg.Connection, conversation_id: uuid.UUID) -> asyncpg.Record | None:
    query = "SELECT id, title, created_at FROM conversations WHERE id = $1;"
    return await conn.fetchrow(query, conversation_id)

async def update_conversation(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None, **kwargs) -> None:
    """Updates a conversation. Pass columns to update as keyword arguments (e.g., title='New')."""
    if conn:
        return await _update_conversation(conn, conversation_id, kwargs)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _update_conversation(conn, conversation_id, kwargs)

async def _update_conversation(conn: asyncpg.Connection, conversation_id: uuid.UUID, updates: dict) -> None:
    if not updates:
        logger.warning("update_conversation called with no columns to update for ID: %s", conversation_id)
        return
    
    valid_columns = {"title"}
    set_clauses = []
    args = []
    idx = 1
    
    for col, val in updates.items():
        if col in valid_columns:
            set_clauses.append(f"{col} = ${idx}")
            args.append(val)
            idx += 1
            
    if not set_clauses:
        logger.warning("update_conversation called with no valid columns to update for ID: %s", conversation_id)
        return
        
    args.append(conversation_id)
    query = f"UPDATE conversations SET {', '.join(set_clauses)} WHERE id = ${idx};"
    await conn.execute(query, *args)
    logger.info("Updated conversation ID: %s with fields: %s", conversation_id, list(updates.keys()))

async def delete_conversation(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> None:
    """Deletes a conversation and all its messages (via ON DELETE CASCADE)."""
    if conn:
        return await _delete_conversation(conn, conversation_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _delete_conversation(conn, conversation_id)

async def _delete_conversation(conn: asyncpg.Connection, conversation_id: uuid.UUID) -> None:
    query = "DELETE FROM conversations WHERE id = $1;"
    await conn.execute(query, conversation_id)
    logger.info("Deleted conversation with ID: %s", conversation_id)