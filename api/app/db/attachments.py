import logging
import uuid
import asyncpg
from app.db.connection import with_connection

logger = logging.getLogger(__name__)

@with_connection
async def create_attachment(
    filename: str,
    mime_type: str,
    data: bytes,
    conn: asyncpg.Connection | None = None
) -> uuid.UUID:
    """Stores a raw file blob. Size is measured server-side from the actual bytes received."""
    query = """
        INSERT INTO attachments (mime_type, filename, size, data)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
    """
    row = await conn.fetchrow(query, mime_type, filename, len(data), data)
    logger.info("Created new attachment with ID: %s (Type: %s, Size: %d bytes)", row['id'], mime_type, len(data))
    return row['id']

@with_connection
async def fetch_attachment(
    attachment_id: uuid.UUID,
    conn: asyncpg.Connection | None = None
) -> dict | None:
    """Fetches a single attachment including its raw bytes (for the download endpoint)."""
    query = "SELECT id, mime_type, filename, size, data FROM attachments WHERE id = $1;"
    record = await conn.fetchrow(query, attachment_id)
    return dict(record) if record else None

@with_connection
async def fetch_attachment_metadata(
    ids: list[uuid.UUID],
    conn: asyncpg.Connection | None = None
) -> list[dict]:
    """
    Fetches metadata (no bytes) for a batch of attachment IDs.
    Returns only the IDs that exist; the caller detects missing ones by count.
    Ordering is not guaranteed — the caller restores the user's order.
    """
    query = "SELECT id, mime_type, filename, size FROM attachments WHERE id = ANY($1);"
    records = await conn.fetch(query, ids)
    logger.info("Fetched metadata for %d of %d requested attachments.", len(records), len(ids))
    return [dict(r) for r in records]

@with_connection
async def fetch_attachment_data(
    ids: list[uuid.UUID],
    conn: asyncpg.Connection | None = None
) -> dict[str, bytes]:
    """
    Fetches raw bytes for a batch of attachment IDs.
    Keyed by the STRING form of the UUID to match the string ids stored
    inside messages.attachments JSONB (direct lookup, no conversion dance).
    """
    query = "SELECT id, data FROM attachments WHERE id = ANY($1);"
    records = await conn.fetch(query, ids)
    return {str(r['id']): r['data'] for r in records}

@with_connection
async def delete_orphaned_attachments(
    conn: asyncpg.Connection | None = None
) -> int:
    """
    Deletes blobs older than 24 hours that no message references.
    Lazily invoked by the caller (upload endpoint), mirroring delete_expired_sessions.
    Returns the number of purged rows.
    """
    query = """
        DELETE FROM attachments a
        WHERE a.created_at < NOW() - INTERVAL '24 hours'
          AND NOT EXISTS (
              SELECT 1
              FROM messages m,
                   jsonb_array_elements(m.attachments) AS att
              WHERE m.attachments <> '[]'::jsonb
                AND (att->>'id')::uuid = a.id
          )
        RETURNING id;
    """
    records = await conn.fetch(query)
    logger.info("Purged %d orphaned attachments.", len(records))
    return len(records)