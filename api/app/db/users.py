import logging
import uuid
from datetime import datetime
import asyncpg
from app.db.connection import with_connection

logger = logging.getLogger(__name__)

@with_connection
async def fetch_user_by_username(username: str, conn: asyncpg.Connection | None = None) -> dict | None:
    """Fetches a user by username."""
    query = "SELECT id, username, password_hash, is_active, created_at FROM users WHERE username = $1;"
    record = await conn.fetchrow(query, username)
    if record:
        return dict(record)
    return None

@with_connection
async def fetch_user_by_id(user_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> dict | None:
    """Fetches a user by ID."""
    query = "SELECT id, username, password_hash, is_active, created_at FROM users WHERE id = $1;"
    record = await conn.fetchrow(query, user_id)
    if record:
        return dict(record)
    return None

@with_connection
async def fetch_all_users(conn: asyncpg.Connection | None = None) -> list[dict]:
    """Fetches all users."""
    query = "SELECT id, username, is_active, created_at FROM users ORDER BY created_at DESC;"
    records = await conn.fetch(query)
    return [dict(r) for r in records]

@with_connection
async def create_user(username: str, password_hash: str, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """Creates a new user. Returns the created user ID."""
    query = """
        INSERT INTO users (username, password_hash)
        VALUES ($1, $2)
        RETURNING id;
    """
    row = await conn.fetchrow(query, username, password_hash)
    logger.info("Created user ID: %s (Username: %s)", row['id'], username)
    return row['id']

@with_connection
async def update_password(user_id: uuid.UUID, new_password_hash: str, conn: asyncpg.Connection | None = None) -> None:
    """Updates a user's password hash."""
    query = "UPDATE users SET password_hash = $1 WHERE id = $2;"
    await conn.execute(query, new_password_hash, user_id)
    logger.info("Updated password hash for user ID: %s", user_id)

@with_connection
async def set_user_active_status(user_id: uuid.UUID, is_active: bool, conn: asyncpg.Connection | None = None) -> None:
    """Enables or disables a user account."""
    query = "UPDATE users SET is_active = $1 WHERE id = $2;"
    await conn.execute(query, is_active, user_id)
    logger.info("Set user %s active status to %s", user_id, is_active)

@with_connection
async def create_session(user_id: uuid.UUID, expires_at: datetime, conn: asyncpg.Connection | None = None) -> uuid.UUID:
    """Creates a new session. Returns the session ID."""
    query = """
        INSERT INTO sessions (user_id, expires_at)
        VALUES ($1, $2)
        RETURNING id;
    """
    row = await conn.fetchrow(query, user_id, expires_at)
    logger.info("Created session ID: %s for user ID: %s", row['id'], user_id)
    return row['id']

@with_connection
async def fetch_session(session_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> dict | None:
    """Fetches a session by ID."""
    query = "SELECT id, user_id, expires_at, created_at FROM sessions WHERE id = $1;"
    record = await conn.fetchrow(query, session_id)
    if record:
        return dict(record)
    return None

@with_connection
async def delete_session(session_id: uuid.UUID, conn: asyncpg.Connection | None = None) -> None:
    """Deletes a specific session (logout)."""
    query = "DELETE FROM sessions WHERE id = $1;"
    await conn.execute(query, session_id)
    logger.info("Deleted session ID: %s", session_id)

@with_connection
async def delete_all_sessions_for_user(user_id: uuid.UUID, exclude_session_id: uuid.UUID | None = None, conn: asyncpg.Connection | None = None) -> None:
    """Deletes all sessions for a user (force logout), optionally keeping one alive."""
    if exclude_session_id:
        query = "DELETE FROM sessions WHERE user_id = $1 AND id != $2;"
        await conn.execute(query, user_id, exclude_session_id)
        logger.info("Deleted sessions for user %s excluding %s", user_id, exclude_session_id)
    else:
        query = "DELETE FROM sessions WHERE user_id = $1;"
        await conn.execute(query, user_id)
        logger.info("Deleted all sessions for user ID: %s", user_id)

@with_connection
async def delete_expired_sessions(conn: asyncpg.Connection | None = None) -> None:
    """Deletes all expired sessions from the database."""
    query = "DELETE FROM sessions WHERE expires_at < NOW();"
    result = await conn.execute(query)
    if result != "DELETE 0":
        logger.info("Cleaned up expired sessions: %s", result)