import logging
import uuid
import asyncpg
from app.db.connection import with_connection

logger = logging.getLogger(__name__)

@with_connection
async def create_preset(name: str, model: str | None, parameters: dict, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """Creates a new generation preset. Returns the created preset ID."""
    query = """
        INSERT INTO generation_presets (name, model, parameters)
        VALUES ($1, $2, $3)
        RETURNING id;
    """
    row = await conn.fetchrow(query, name, model, parameters)
    logger.info("Created generation preset ID: %s (Name: %s)", row['id'], name)
    return row['id']

@with_connection
async def fetch_all_presets(conn: asyncpg.Connection | None = None) -> list[dict]:
    """Fetches all generation presets."""
    query = "SELECT id, name, model, parameters, created_at, updated_at FROM generation_presets ORDER BY created_at DESC;"
    records = await conn.fetch(query)
    logger.info("Fetched %d generation presets", len(records))
    return [dict(r) for r in records]

@with_connection
async def fetch_preset(preset_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> dict | None:
    """Fetches a single generation preset by ID."""
    query = "SELECT id, name, model, parameters, created_at, updated_at FROM generation_presets WHERE id = $1;"
    record = await conn.fetchrow(query, preset_id)
    if record:
        return dict(record)
    return None

@with_connection
async def update_preset(preset_id: uuid.UUID, conn: asyncpg.Connection | None = None, **kwargs) -> None:
    """Updates a generation preset. Pass columns to update as keyword arguments."""
    updates = kwargs
    if not updates:
        logger.warning("update_preset called with no columns to update for ID: %s", preset_id)
        return
    
    valid_columns = {"name", "model", "parameters"}
    set_clauses = []
    args = []
    idx = 1
    
    for col, val in updates.items():
        if col in valid_columns:
            set_clauses.append(f"{col} = ${idx}")
            args.append(val)
            idx += 1
            
    if not set_clauses:
        logger.warning("update_preset called with no valid columns to update for ID: %s", preset_id)
        return
        
    set_clauses.append(f"updated_at = clock_timestamp()")
    
    args.append(preset_id)
    query = f"UPDATE generation_presets SET {', '.join(set_clauses)} WHERE id = ${idx};"
    await conn.execute(query, *args)
    logger.info("Updated generation preset ID: %s with fields: %s", preset_id, list(updates.keys()))

@with_connection
async def delete_preset(preset_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> None:
    """Deletes a generation preset."""
    query = "DELETE FROM generation_presets WHERE id = $1;"
    await conn.execute(query, preset_id)
    logger.info("Deleted generation preset with ID: %s", preset_id)