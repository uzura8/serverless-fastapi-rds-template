from __future__ import annotations
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column


from .base import BaseORM
from app.schemas.task import TaskSchema
from app.schemas.done import DoneSchema


class TaskModel(BaseORM):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # one-to-one リレーションは Mapped[Optional[RelatedModel]]
    done: Mapped[Optional[DoneModel]] = relationship(
        'DoneModel',         # 文字列 forward-ref
        back_populates='task',
        uselist=False,
        lazy='joined',       # 常に JOIN してロード → 後から遅延ロードしない
        cascade='all, delete-orphan',
    )
    # cascade='all': save-update, merge, refresh-expire, expunge, delete をまとめたエイリアス
    #   save-update: TaskModel を保存すると DoneModel も保存される
    #   merge: TaskModel をマージすると DoneModel もマージされる
    #   refresh-expire: TaskModel をリフレッシュすると DoneModel もリフレッシュされる
    #   expunge: TaskModel を削除すると DoneModel も削除される
    #   delete: TaskModel を削除すると DoneModel も削除される
    # cascade='delete-orphan': TaskModel が削除されたときに DoneModel も削除される

    @classmethod
    def from_entity(cls, task_entity: TaskSchema) -> TaskModel:
        """
        Pydantic の Task（または TaskBase）を受け取り、
        ORM インスタンスを生成して返す。
        たとえば create のときなどに使う。
        """
        return cls(
            id=task_entity.id if hasattr(task_entity, "id") else None,
            title=task_entity.title,
        )

    def to_entity(self) -> TaskSchema:
        """
        この ORM インスタンスを Pydantic の Task に変換する。
        `Task.Config.orm_mode = True` が有効なので、self をそのまま渡せば OK。
        """
        return TaskSchema.model_validate(self)

    def update(self, task_entity: TaskSchema) -> None:
        """
        すでにフェッチ済みの ORM インスタンスの属性を
        Pydantic Task の値で上書きする。
        """
        self.title = task_entity.title
        # done は別テーブル（DoneModel）で管理しているので、このメソッドでは触らない


class DoneModel(BaseORM):
    __tablename__ = "dones"

    # id を外部キーかつ主キーに
    id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # TaskModel への逆リレーション
    task: Mapped[TaskModel] = relationship(
        "TaskModel",
        back_populates="done",
        uselist=False,
    )

    @classmethod
    def from_entity(cls, task_entity: TaskSchema) -> DoneSchema:
        return cls(
            id=task_entity.id if hasattr(task_entity, "id") else None,
            task=TaskModel.from_entity(task_entity),
        )

    def to_entity(self) -> DoneSchema:
        return DoneSchema.model_validate(self)

    def update(self, done: DoneSchema) -> None:
        self.id = done.id
