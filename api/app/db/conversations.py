import logging
import uuid
import asyncpg
from app.db.connection import with_connection

logger = logging.getLogger(__name__)

@with_connection
async def create_conversation(title: str | None, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """Creates a new conversation in the database."""
    query = "INSERT INTO conversations (title) VALUES ($1) RETURNING id;"
    row = await conn.fetchrow(query, title)
    logger.info("Created new conversation with ID: %s", row['id'])
    return row['id']

@with_connection
async def fetch_conversation(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> dict | None:
    """Fetches a single conversation by its ID."""
    query = "SELECT id, title, active_leaf_id, created_at FROM conversations WHERE id = $1;"
    record = await conn.fetchrow(query, conversation_id)
    return dict(record) if record else None

@with_connection
async def fetch_all_conversations(conn: asyncpg.Connection | None = None) -> list[dict]:
    """Fetches all conversations, ordered by newest first."""
    query = "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC;"
    records = await conn.fetch(query)
    return [dict(r) for r in records]

@with_connection
async def update_conversation(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None, **kwargs) -> None:
    """Updates a conversation. Pass columns to update as keyword arguments (e.g., title='New')."""
    updates = kwargs
    if not updates:
        logger.warning("update_conversation called with no columns to update for ID: %s", conversation_id)
        return
    
    valid_columns = {"title", "active_leaf_id"}
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

@with_connection
async def delete_conversation(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> None:
    """Deletes a conversation and all its messages (via ON DELETE CASCADE)."""
    query = "DELETE FROM conversations WHERE id = $1;"
    await conn.execute(query, conversation_id)
    logger.info("Deleted conversation with ID: %s", conversation_id)