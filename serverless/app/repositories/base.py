from typing import Generic, Type, TypeVar, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import (
    DeclarativeMeta,
    selectinload,
    joinedload,
)
from app.exceptions import NotFound, AlreadyExists, DatabaseError


# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
SchemaType = TypeVar("SchemaType")


class BaseRepository(Generic[ModelType, SchemaType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def commit_and_refresh(self, instance: ModelType) -> ModelType:
        """
        1) トランザクションをコミット
        2) IntegrityError をエラ―コードで分岐してラップ
           - 1452 → NotFoundError（FK違反）
           - 1062 → AlreadyExistsError（UNIQUE違反）
           - それ以外 → DatabaseError
        3) コミット成功なら session.refresh → インスタンスを返す
        """
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            orig = e.orig
            code = orig.args[0] if (
                hasattr(orig, "args") and orig.args) else None

            if code == 1452:
                raise NotFound(
                    f"Parent record not found ({orig!r})") from e
            elif code == 1062:
                raise AlreadyExists(f"Duplicate entry ({orig!r})") from e
            else:
                raise DatabaseError(
                    "Unexpected integrity error", original_exception=e) from e

        except Exception as e:
            await self.session.rollback()
            raise DatabaseError("Unexpected database error",
                                original_exception=e) from e

        await self.session.refresh(instance)
        return instance

    async def get(
        self,
        record_id: int,
        load_relations: list[str] = None
    ) -> Optional[ModelType]:
        """Get a record by its ID."""
        query = select(self.model).filter_by(id=record_id)
        if load_relations:
            for relation in load_relations:
                if '.' in relation:
                    # nested relation: e.g. "parent.child"
                    parts = relation.split('.')
                    current_model = self.model
                    option = None
                    for part in parts:
                        attr = getattr(current_model, part)
                        current_model = attr.property.mapper.class_
                        if option is None:
                            option = joinedload(attr)
                        else:
                            option = option.joinedload(attr)
                    query = query.options(option)
                else:
                    query = query.options(selectinload(
                        getattr(self.model, relation)))

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_all(
        self,
        load_relations: list[str] = None
    ) -> list[ModelType]:
        """Get all records."""
        query = select(self.model)
        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(
                    getattr(self.model, relation)))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, schema: SchemaType) -> ModelType:
        """
        schema.model_dump() で dict を取り出し、
        model のコンストラクタに展開する。
        """
        data = schema.model_dump(exclude_unset=True)  # or .dict()
        new_record = self.model(**data)               # <- モデル層にスキーマ依存なし
        self.session.add(new_record)
        return await self.commit_and_refresh(new_record)

    async def update(
        self,
        record_id: int,
        schema: SchemaType
    ) -> Optional[ModelType]:
        """Update a record."""
        query = await self.session.execute(
            select(self.model).filter_by(id=record_id)
        )
        record = query.scalar_one_or_none()
        if not record:
            return None

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        # for key, value in schema.dict(exclude_unset=True).items():
        #     setattr(record, key, value)
        return await self.commit_and_refresh(record)

    async def delete(self, record_id: int) -> bool:
        """Delete a record."""
        query = await self.session.execute(
            select(self.model).filter_by(id=record_id)
        )
        record = query.scalar_one_or_none()
        if not record:
            return False
        await self.session.delete(record)
        await self.session.commit()
        return True
