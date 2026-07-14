import logging
import uuid
import asyncpg
from app.db.connection import get_pool

logger = logging.getLogger(__name__)

async def create_message(
    conversation_id: uuid.UUID, 
    role: str, 
    parent_id: uuid.UUID | None = None, 
    content: str | None = None, 
    status: str = 'pending',
    creation_data: dict | None = None,
    conn: asyncpg.Connection | None = None
) -> uuid.UUID:
    """Creates a new message in the database."""
    if conn:
        return await _create_message(conn, conversation_id, role, parent_id, content, status, creation_data)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _create_message(conn, conversation_id, role, parent_id, content, status, creation_data)

async def _create_message(
    conn: asyncpg.Connection, 
    conversation_id: uuid.UUID, 
    role: str, 
    parent_id: uuid.UUID | None, 
    content: str | None, 
    status: str,
    creation_data: dict | None
) -> uuid.UUID:
    query = """
        INSERT INTO messages (conversation_id, role, parent_id, content, status, creation_data) 
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING id;
    """
    row = await conn.fetchrow(query, conversation_id, role, parent_id, content, status, creation_data)
    logger.info("Created new message with ID: %s (Role: %s)", row['id'], role)
    return row['id']

async def fetch_message(message_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> asyncpg.Record | None:
    """Fetches a single message by its ID."""
    if conn:
        return await _fetch_message(conn, message_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _fetch_message(conn, message_id)

async def _fetch_message(conn: asyncpg.Connection, message_id: uuid.UUID) -> asyncpg.Record | None:
    query = "SELECT id, conversation_id, role, parent_id, content, status, error_data, metadata, creation_data, created_at FROM messages WHERE id = $1;"
    return await conn.fetchrow(query, message_id)

async def update_message(message_id: uuid.UUID, conn: asyncpg.Connection | None = None, **kwargs) -> None:
    """Updates a message. Pass columns to update as keyword arguments (e.g., content='...', status='complete')."""
    if conn:
        return await _update_message(conn, message_id, kwargs)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _update_message(conn, message_id, kwargs)

async def _update_message(conn: asyncpg.Connection, message_id: uuid.UUID, updates: dict) -> None:
    if not updates:
        logger.warning("update_message called with no columns to update for ID: %s", message_id)
        return
    
    valid_columns = {"parent_id", "role", "content", "status", "error_data", "metadata", "creation_data"}
    set_clauses = []
    args = []
    idx = 1
    
    for col, val in updates.items():
        if col in valid_columns:
            set_clauses.append(f"{col} = ${idx}")
            args.append(val)
            idx += 1
            
    if not set_clauses:
        logger.warning("update_message called with no valid columns to update for ID: %s", message_id)
        return
        
    args.append(message_id)
    query = f"UPDATE messages SET {', '.join(set_clauses)} WHERE id = ${idx};"
    await conn.execute(query, *args)
    logger.info("Updated message ID: %s with fields: %s", message_id, list(updates.keys()))

async def delete_message(message_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> None:
    """Deletes a message and its children (via ON DELETE CASCADE)."""
    if conn:
        return await _delete_message(conn, message_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _delete_message(conn, message_id)

async def _delete_message(conn: asyncpg.Connection, message_id: uuid.UUID) -> None:
    query = "DELETE FROM messages WHERE id = $1;"
    await conn.execute(query, message_id)
    logger.info("Deleted message with ID: %s", message_id)

async def fetch_message_history(message_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> list[asyncpg.Record]:
    """
    Traverses the tree upwards from the given message ID to the root.
    Returns an ordered list of messages (root first, target last).
    """
    if conn:
        return await _fetch_message_history(conn, message_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _fetch_message_history(conn, message_id)

async def _fetch_message_history(conn: asyncpg.Connection, message_id: uuid.UUID) -> list[asyncpg.Record]:
    # Recursive CTE to walk up the parent_id chain tracking depth
    query = """
        WITH RECURSIVE history AS (
            SELECT id, conversation_id, role, parent_id, content, status, error_data, metadata, creation_data, created_at, 1 as depth
            FROM messages
            WHERE id = $1
            UNION ALL
            SELECT m.id, m.conversation_id, m.role, m.parent_id, m.content, m.status, m.error_data, m.metadata, m.creation_data, m.created_at, h.depth + 1
            FROM messages m
            JOIN history h ON m.id = h.parent_id
        )
        SELECT id, role, content, status, error_data, metadata, creation_data, created_at FROM history ORDER BY depth DESC;
    """
    records = await conn.fetch(query, message_id)
    logger.info("Fetched history for message ID: %s (Length: %d)", message_id, len(records))
    return records

async def fetch_conversation_messages(conversation_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> list[asyncpg.Record]:
    """Fetches all messages for a conversation as a flat list, ordered by creation time."""
    if conn:
        return await _fetch_conversation_messages(conn, conversation_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        return await _fetch_conversation_messages(conn, conversation_id)

async def _fetch_conversation_messages(conn: asyncpg.Connection, conversation_id: uuid.UUID) -> list[asyncpg.Record]:
    query = """
        SELECT id, conversation_id, role, parent_id, content, status, error_data, metadata, creation_data, created_at 
        FROM messages 
        WHERE conversation_id = $1 
        ORDER BY created_at ASC;
    """
    records = await conn.fetch(query, conversation_id)
    logger.info("Fetched %d messages for conversation ID: %s", len(records), conversation_id)
    return records