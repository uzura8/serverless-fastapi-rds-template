import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_list_items(ac):
    response = await ac.get(f"{settings.API_V1_STR}/items/")
    assert response.status_code == 200
    # data = await response.json()
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data == [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
