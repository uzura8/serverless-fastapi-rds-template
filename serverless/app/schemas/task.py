from typing import Optional
from pydantic import Field
from .base import BaseSchema


class TaskBaseSchema(BaseSchema):
    title: Optional[str] = Field(
        default=None,
        json_schema_extra={'example': 'クリーニングを取りに行く'}
    )


class TaskSchema(TaskBaseSchema):
    id: int
    done: bool = Field(False, description='完了フラグ')


class TaskCreateSchema(TaskBaseSchema):
    pass
