from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database import get_session
from app.exceptions import NotFound, AlreadyExists
from app.models import DoneORM
from .base import BaseRepository
from .task import TaskORM


class DoneRepository(BaseRepository[DoneORM, None]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(DoneORM, session)

    async def create_by_task_id(self, task_id: int) -> DoneORM:
        """
        Create a Done record by task_id.
        """

        task = (
            await self.session.execute(
                select(TaskORM).filter_by(id=task_id)
            )
        ).scalar_one_or_none()
        if task is None:
            raise NotFound(f"Task(id={task_id}) not found")

        existing = (
            await self.session.execute(
                select(DoneORM).filter_by(id=task_id)
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise AlreadyExists('done', task_id)

        done = DoneORM(id=task_id)
        self.session.add(done)
        await self.session.commit()
        await self.session.refresh(done)
        return done
