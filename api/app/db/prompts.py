import logging
import uuid
import asyncpg
from app.db.connection import with_connection

logger = logging.getLogger(__name__)

@with_connection
async def create_prompt(name: str, content: str, role: str, description: str | None = None, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """Creates a new prompt. Returns the created prompt dict."""
    query = """
        INSERT INTO prompts (name, content, role, description)
        VALUES ($1, $2, $3, $4)
        RETURNING id, name, content, role, description, created_at, updated_at;
    """
    row = await conn.fetchrow(query, name, content, role, description)
    logger.info("Created prompt ID: %s (Name: %s, Role: %s)", row['id'], name, role)
    return row['id']

@with_connection
async def fetch_all_prompts(role: str | None = None, conn: asyncpg.Connection | None = None) -> list[dict]:
    """Fetches all prompts, optionally filtered by role."""
    if role:
        query = "SELECT id, name, content, role, description, created_at, updated_at FROM prompts WHERE role = $1 ORDER BY created_at DESC;"
        records = await conn.fetch(query, role)
    else:
        query = "SELECT id, name, content, role, description, created_at, updated_at FROM prompts ORDER BY created_at DESC;"
        records = await conn.fetch(query)
    
    logger.info("Fetched %d prompts (Role filter: %s)", len(records), role)
    return [dict(r) for r in records]

@with_connection
async def fetch_prompt(prompt_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> dict | None:
    """Fetches a single prompt by ID."""
    query = "SELECT id, name, content, role, description, created_at, updated_at FROM prompts WHERE id = $1;"
    record = await conn.fetchrow(query, prompt_id)
    if record:
        return dict(record)
    return None

@with_connection
async def update_prompt(prompt_id: uuid.UUID, conn: asyncpg.Connection | None = None, **kwargs) -> None:
    """Updates a prompt. Pass columns to update as keyword arguments (e.g., name='New'). Returns updated prompt dict."""
    updates = kwargs
    if not updates:
        logger.warning("update_prompt called with no columns to update for ID: %s", prompt_id)
        return
    
    valid_columns = {"name", "content", "role", "description"}
    set_clauses = []
    args = []
    idx = 1
    
    for col, val in updates.items():
        if col in valid_columns:
            set_clauses.append(f"{col} = ${idx}")
            args.append(val)
            idx += 1
            
    if not set_clauses:
        logger.warning("update_prompt called with no valid columns to update for ID: %s", prompt_id)
        return
        
    # Always update the updated_at timestamp
    set_clauses.append(f"updated_at = NOW()")
    
    args.append(prompt_id)
    query = f"UPDATE prompts SET {', '.join(set_clauses)} WHERE id = ${idx};"
    await conn.execute(query, *args)
    logger.info("Updated prompt ID: %s with fields: %s", prompt_id, list(updates.keys()))

@with_connection
async def delete_prompt(prompt_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> None:
    """Deletes a prompt."""
    query = "DELETE FROM prompts WHERE id = $1;"
    await conn.execute(query, prompt_id)
    logger.info("Deleted prompt with ID: %s", prompt_id)