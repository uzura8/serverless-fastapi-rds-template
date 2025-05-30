import pytest
import pytest_asyncio
from app.main import app

# from httpx import AsyncClient
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


# @pytest.fixture(scope="function")
@pytest_asyncio.fixture  # pytest-asyncioを使う場合
async def ac():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # async with AsyncClient(app=app, base_url="http://test", headers=headers) as c:
    #     yield c
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=headers,
    ) as client:
        yield client
