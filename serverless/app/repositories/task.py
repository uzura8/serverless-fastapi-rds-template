from typing import Optional
from fastapi import Depends
from app.database import get_session
from app.models import TaskModel, DoneModel
from app.schemas.task import TaskCreateSchema, TaskSchema
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository


class TaskRepository(BaseRepository[TaskModel, TaskCreateSchema]):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        BaseRepository.__init__ は (model, session) の 2 引数を取るので、
        TaskRepository では TaskModel を model に渡す。
        """
        super().__init__(TaskModel, session)

    async def list_with_done(self) -> list[TaskSchema]:
        """
        タスク一覧を取得しつつ「完了済みかどうか」を boolean で返す。
        戻り値は (task_id, title, done_flag) のタプルのリスト。
        """
        stmt = (
            select(
                TaskModel.id,
                TaskModel.title,
                # DoneModel.id が NULL でなければ done=True
                DoneModel.id.isnot(None).label('done'),
            )
            # TaskModel と DoneModel を外部結合
            # .outerjoin(DoneModel, DoneModel.id == TaskModel.id)
            .outerjoin(TaskModel.done)
        )
        result: Result = await self.session.execute(stmt)
        return result.all()

    async def get_with_done(self, task_id: int) -> Optional[tuple[int, str, bool]]:
        stmt = (
            select(
                TaskModel.id,
                TaskModel.title,
                DoneModel.id.isnot(None).label('done'),
            )
            .outerjoin(TaskModel.done)
            # .outerjoin(DoneModel, DoneModel.id == TaskModel.id)
            .filter(TaskModel.id == task_id)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        return row
