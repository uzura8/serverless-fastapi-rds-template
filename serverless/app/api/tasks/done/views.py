from app.routes import LoggingRoute
from typing import Annotated
from fastapi import APIRouter, Depends, status
from .schemas import PutDoneResponse
from .use_case import (
    UpdateDone,
    DeleteDone
)

router = APIRouter(
    prefix='/done', route_class=LoggingRoute
)


@router.put('', response_model=PutDoneResponse)
async def mark_task_as_done(
    task_id: int,
    use_case: Annotated[
        UpdateDone, Depends(UpdateDone)
    ],
) -> PutDoneResponse:
    return PutDoneResponse.model_validate(
        await use_case.execute(task_id=task_id)
    )


@router.delete(
    '',
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def unmark_task_as_done(
    task_id: int,
    use_case: Annotated[
        DeleteDone, Depends(DeleteDone)
    ],
) -> None:
    return PutDoneResponse.model_validate(
        await use_case.execute(task_id=task_id)
    )
