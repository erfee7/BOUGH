import pytest_asyncio
import asyncpg
from app.db.connection import init_pool, close_pool, get_pool

@pytest_asyncio.fixture(scope="session")
async def db_pool():
    """Initializes the connection pool once for the entire test session."""
    await init_pool()
    yield get_pool()
    await close_pool()

@pytest_asyncio.fixture
async def db_transaction(db_pool: asyncpg.Pool):
    """
    Yields a connection with an active transaction.
    Rolls back the transaction after the test completes to ensure a clean state.
    """
    async with db_pool.acquire() as conn:
        tx = conn.transaction()
        await tx.start()
        try:
            yield conn
        finally:
            await tx.rollback()