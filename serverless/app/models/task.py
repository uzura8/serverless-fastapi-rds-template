from __future__ import annotations
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column


from .base import BaseORM
from app.schemas.task import Task
from app.schemas.done import Done


class TaskORM(BaseORM):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # one-to-one リレーションは Mapped[Optional[RelatedModel]]
    done: Mapped[Optional[DoneORM]] = relationship(
        'DoneORM',         # 文字列 forward-ref
        back_populates='task',
        uselist=False,
        lazy='joined',       # 常に JOIN してロード → 後から遅延ロードしない
        cascade='all, delete-orphan',
    )
    # cascade='all': save-update, merge, refresh-expire, expunge, delete をまとめたエイリアス
    #   save-update: TaskORM を保存すると DoneORM も保存される
    #   merge: TaskORM をマージすると DoneORM もマージされる
    #   refresh-expire: TaskORM をリフレッシュすると DoneORM もリフレッシュされる
    #   expunge: TaskORM を削除すると DoneORM も削除される
    #   delete: TaskORM を削除すると DoneORM も削除される
    # cascade='delete-orphan': TaskORM が削除されたときに DoneORM も削除される

    @classmethod
    def from_entity(cls, task_entity: Task) -> TaskORM:
        """
        Pydantic の Task（または TaskBase）を受け取り、
        ORM インスタンスを生成して返す。
        たとえば create のときなどに使う。
        """
        return cls(
            id=task_entity.id if hasattr(task_entity, "id") else None,
            title=task_entity.title,
        )

    def to_entity(self) -> Task:
        """
        この ORM インスタンスを Pydantic の Task に変換する。
        `Task.Config.orm_mode = True` が有効なので、self をそのまま渡せば OK。
        """
        return Task.model_validate(self)

    def update(self, task_entity: Task) -> None:
        """
        すでにフェッチ済みの ORM インスタンスの属性を
        Pydantic Task の値で上書きする。
        """
        self.title = task_entity.title
        # done は別テーブル（DoneORM）で管理しているので、このメソッドでは触らない


class DoneORM(BaseORM):
    __tablename__ = "dones"

    # id を外部キーかつ主キーに
    id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # TaskORM への逆リレーション
    task: Mapped[TaskORM] = relationship(
        "TaskORM",
        back_populates="done",
        uselist=False,
    )

    @classmethod
    def from_entity(cls, task_entity: Task) -> Done:
        return cls(
            id=task_entity.id if hasattr(task_entity, "id") else None,
            task=TaskORM.from_entity(task_entity),
        )

    def to_entity(self) -> Done:
        return Done.model_validate(self)

    def update(self, done: Done) -> None:
        self.id = done.id
