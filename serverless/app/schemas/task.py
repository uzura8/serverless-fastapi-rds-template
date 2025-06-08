from typing import Optional
from pydantic import Field
from .base import BaseSchema


class TaskBase(BaseSchema):
    title: Optional[str] = Field(
        default=None,
        json_schema_extra={'example': 'クリーニングを取りに行く'}
    )


class Task(TaskBase):
    id: int
    done: bool = Field(False, description='完了フラグ')


class TaskCreate(TaskBase):
    pass
