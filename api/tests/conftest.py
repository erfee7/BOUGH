import pytest_asyncio
import pytest
import asyncpg
import uuid
from app.db.connection import init_pool, close_pool, get_pool
from app.main import app
from app.security import get_current_user

# --- Database Core Fixtures ---

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

# --- Shared API Test Utilities ---

class FakePool:
    """A fake connection pool that simply yields the active test transaction connection."""
    def __init__(self, conn):
        self.conn = conn

    class ConnectionContextManager:
        def __init__(self, conn):
            self.conn = conn
        async def __aenter__(self):
            return self.conn
        async def __aexit__(self, exc_type, exc, tb):
            pass

    def acquire(self):
        return self.ConnectionContextManager(self.conn)

@pytest.fixture
def mock_pool(db_transaction):
    """
    Provides a FakePool instance bound to the current test's transactional connection.
    Use this to patch 'get_pool' in router modules.
    """
    return FakePool(db_transaction)

# --- Auth Bypass Fixture ---

@pytest.fixture(autouse=True)
def mock_authentication():
    """Automatically bypasses authentication for all tests by default."""
    mock_user = {
        "id": uuid.uuid4(),
        "username": "autouse_testuser",
        "password_hash": "dummy_hash",
        "is_active": True,
        "created_at": "2023-01-01T00:00:00+00:00"
    }
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()