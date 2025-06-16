from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.routes import LoggingRoute
from app.schemas.task import TaskSchema
from .schemas import (
    GetTasksResponse,
    GetTaskResponse,
    PostTaskRequest,
    PostTaskResponse,
    PutTaskRequest,
    PutTaskResponse
)
from .use_case import (
    ListTasks,
    GetTask,
    CreateTask,
    UpdateTask,
    DeleteTask
)
from .done.views import (
    router as done_router,
)

router = APIRouter(prefix='/tasks', route_class=LoggingRoute)


@router.get('', response_model=GetTasksResponse)
async def get_tasks(
    use_case: Annotated[
        ListTasks, Depends(ListTasks)
    ]
) -> GetTasksResponse:
    return GetTasksResponse(
        tasks=[TaskSchema.model_validate(t)
               for t in await use_case.execute()]
    )


@router.get('/{task_id}', response_model=GetTaskResponse)
async def get_task(
    task_id: int,
    use_case: Annotated[
        GetTask, Depends(GetTask)
    ],
) -> GetTaskResponse:
    result = await use_case.execute(
        task_id=task_id
    )
    return GetTaskResponse.model_validate(result)


@router.post('', response_model=PostTaskResponse)
async def create_task(
    data: PostTaskRequest,
    use_case: Annotated[
        CreateTask, Depends(CreateTask)
    ],
) -> PostTaskResponse:
    saved = await use_case.execute(data)
    result = {
        'id': saved.id,
        'title': saved.title,
        'done': saved.done is not None,
    }
    return PostTaskResponse.model_validate(result)


@router.put('/{task_id}', response_model=PutTaskResponse)
async def update_task(
    task_id: int,
    data: PutTaskRequest,
    use_case: Annotated[
        UpdateTask, Depends(UpdateTask)
    ],
) -> PutTaskResponse:
    saved = await use_case.execute(task_id, data)
    result = {
        'id': saved.id,
        'title': saved.title,
        'done': saved.done is not None,
    }
    return PostTaskResponse.model_validate(result)


@router.delete(
    '/{task_id}',
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task_id: int,
    use_case: Annotated[
        DeleteTask, Depends(DeleteTask)
    ],
) -> None:
    await use_case.execute(task_id=task_id)

router.include_router(
    done_router, prefix='/{task_id}'
)
