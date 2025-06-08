# tests/test_tasks_endpoints.py

import starlette.status
import pytest
from app.core.config import settings

prefix = settings.API_V1_STR


@pytest.mark.asyncio
async def test_create_and_read(async_client):
    # タスク作成
    response = await async_client.post(
        f'{prefix}/tasks',
        json={'title': 'テストタスク'}
    )
    assert response.status_code == starlette.status.HTTP_200_OK
    data = response.json()
    assert data['title'] == 'テストタスク'
    assert data['done'] is False

    # 作成したタスク一覧を取得
    response = await async_client.get(f'{prefix}/tasks')
    assert response.status_code == starlette.status.HTTP_200_OK
    list_data = response.json()
    assert isinstance(list_data, dict)

    assert 'tasks' in list_data
    tasks = list_data['tasks']
    assert isinstance(tasks, list)
    assert len(tasks) == 1

    # 中身の確認
    first = tasks[0]
    assert first['title'] == 'テストタスク'
    assert first['done'] is False


@pytest.mark.asyncio
async def test_done_flag(async_client):
    # テストのためのタスクを作成
    response = await async_client.post(f"{prefix}/tasks", json={"title": "テストタスク2"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク2"
    task_id = response_obj["id"]

    # 完了フラグを立てる
    response = await async_client.put(f"{prefix}/tasks/{task_id}/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    # 既に完了フラグが立っているので400を返却
    response = await async_client.put(f"{prefix}/tasks/{task_id}/done")
    assert response.status_code == starlette.status.HTTP_400_BAD_REQUEST

    # 完了フラグを外す
    response = await async_client.delete(f"{prefix}/tasks/{task_id}/done")
    assert response.status_code == starlette.status.HTTP_204_NO_CONTENT

    # 既に完了フラグが外れているので404を返却
    response = await async_client.delete(f"{prefix}/tasks/{task_id}/done")
    assert response.status_code == starlette.status.HTTP_404_NOT_FOUND
