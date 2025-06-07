from app.schemas.base import BaseSchema
from app.schemas.task import (
    Task,
    TaskCreate,
)


class GetTasksResponse(BaseSchema):
    tasks: list[Task]


class GetTaskResponse(Task):
    pass


class PostTaskRequest(TaskCreate):
    pass


class PostTaskResponse(Task):
    pass


class PutTaskRequest(TaskCreate):
    pass


class PutTaskResponse(Task):
    pass
