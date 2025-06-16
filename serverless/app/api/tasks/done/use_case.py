from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.exceptions import NotFound
from app.schemas.done import DoneSchema
from app.repositories import DoneRepository


class UpdateDone:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: DoneRepository = Depends(DoneRepository)
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self, task_id: int) -> DoneSchema:
        return await self.repo.create_by_task_id(task_id)


class DeleteDone:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: DoneRepository = Depends(DoneRepository)
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self, task_id: int) -> None:
        done = await self.repo.get(task_id)
        if done is None:
            raise NotFound('done', task_id)
        await self.repo.delete(task_id)
