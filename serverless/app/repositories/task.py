from typing import Optional
from fastapi import Depends
from app.database import get_session
from app.models import TaskORM, DoneORM
from app.schemas.task import TaskCreate, Task
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository


class TaskRepository(BaseRepository[TaskORM, TaskCreate]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        BaseRepository.__init__ は (model, session) の 2 引数を取るので、
        TaskRepository では TaskORM を model に渡す。
        """
        super().__init__(TaskORM, session)

    async def list_with_done(self) -> list[Task]:
        """
        タスク一覧を取得しつつ「完了済みかどうか」を boolean で返す。
        戻り値は (task_id, title, done_flag) のタプルのリスト。
        """
        stmt = (
            select(
                TaskORM.id,
                TaskORM.title,
                # DoneORM.id が NULL でなければ done=True
                DoneORM.id.isnot(None).label('done'),
            )
            # TaskORM と DoneORM を外部結合
            # .outerjoin(DoneORM, DoneORM.id == TaskORM.id)
            .outerjoin(TaskORM.done)
        )
        result: Result = await self.session.execute(stmt)
        return result.all()

    async def get_with_done(self, task_id: int) -> Optional[tuple[int, str, bool]]:
        stmt = (
            select(
                TaskORM.id,
                TaskORM.title,
                DoneORM.id.isnot(None).label('done'),
            )
            .outerjoin(TaskORM.done)
            # .outerjoin(DoneORM, DoneORM.id == TaskORM.id)
            .filter(TaskORM.id == task_id)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        return row
