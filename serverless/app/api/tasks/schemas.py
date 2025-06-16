from app.schemas.base import BaseSchema
from app.schemas.task import (
    TaskSchema,
    TaskCreateSchema,
)


class GetTasksResponse(BaseSchema):
    tasks: list[TaskSchema]


class GetTaskResponse(TaskSchema):
    pass


class PostTaskRequest(TaskCreateSchema):
    pass


class PostTaskResponse(TaskSchema):
    pass


class PutTaskRequest(TaskCreateSchema):
    pass


class PutTaskResponse(TaskSchema):
    pass
