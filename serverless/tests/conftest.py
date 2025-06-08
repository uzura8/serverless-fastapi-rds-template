import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import get_session     # DI 用プロバイダー
from app.main import app
from app.models.base import BaseORM     # DeclarativeBase

# in-memory SQLite
ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    ASYNC_DB_URL, connect_args={"check_same_thread": False}
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# テーブルの作成／破棄


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.drop_all)

# テスト用セッション


@pytest_asyncio.fixture
async def session():
    async with AsyncSessionLocal() as session:
        yield session

# FastAPI の get_session をオーバーライドした AsyncClient


@pytest_asyncio.fixture
async def async_client(session: AsyncSession):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
