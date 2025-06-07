from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.exceptions import NotFound
from app.schemas.task import Task
from app.repositories import TaskRepository


class ListTasks:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: TaskRepository = Depends(TaskRepository),
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self) -> list[Task]:
        return await self.repo.list_with_done()


class GetTask:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: TaskRepository = Depends(TaskRepository),
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self, task_id: int) -> Task:
        task = await self.repo.get_with_done(task_id)
        if task is None:
            raise NotFound('task', task_id)
        return task


class CreateTask:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: TaskRepository = Depends(TaskRepository),
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self, data: Task) -> Task:
        return await self.repo.create(data)


class UpdateTask:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: TaskRepository = Depends(TaskRepository),
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self, task_id: int, data: Task) -> Task:
        saved = await self.repo.get(task_id)
        if saved is None:
            raise NotFound('task', task_id)
        return await self.repo.update(task_id, data)


class DeleteTask:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: TaskRepository = Depends(TaskRepository),
    ) -> None:
        self.session = session
        self.repo = repo

    async def execute(self, task_id: int) -> None:
        task = await self.repo.get(task_id)
        if task is None:
            raise NotFound('task', task_id)
        return await self.repo.delete(task_id)
