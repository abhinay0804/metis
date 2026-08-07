import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from server.app import app
from server.database.connection import get_db
from server.database.models import Base
from server.auth import hash_password

# Test database URL (SQLite for speed and isolation)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)



@pytest.fixture(scope="function")
async def test_db():
    """Create a fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def test_client(test_db):
    """Create a test client with overridden dependencies."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
        
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_user(test_db):
    """Create a test user and return credentials."""
    from server.repositories import UserRepository
    repo = UserRepository(test_db)
    pwd = "TestPassword123"
    user = await repo.create(
        email="test@example.com",
        password_hash=hash_password(pwd),
        full_name="Test User"
    )
    return {"user": user, "email": "test@example.com", "password": pwd}

@pytest.fixture(scope="function")
async def auth_client(test_client, test_user):
    """Return a test client with an active JWT token in the headers."""
    resp = await test_client.post("/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = resp.json()["access_token"]
    test_client.headers.update({"Authorization": f"Bearer {token}"})
    return test_client
