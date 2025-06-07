import logging
from typing import AsyncIterator
from sqlalchemy import Connection, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
from app.exceptions import AppException
from app.models import BaseORM

logger = logging.getLogger(__name__)

# Create engine
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.ENABLE_SQL_LOG  # Output SQL logs to console
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    # expire_on_commit=False,  # True: コミット後に必ず再フェッチし、オブジェクトを更新する
    class_=AsyncSession
)


# ------------------------------------------------------------
# 3) FastAPI などで「セッションが欲しい」ときに使うヘルパー関数
#    - 非同期ジェネレータで AsyncSession を yield する
#    - 例外が発生した場合はロールバックして独自例外を投げる
# ------------------------------------------------------------
async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.exception(e)
            raise AppException() from e


async def create_database_if_not_exist() -> None:

    def create_tables_if_not_exist(
        sync_conn: Connection,
    ) -> None:
        if not inspect(sync_conn.engine).has_table(
            settings.TABLE_TO_CHECK_DB_EXIST
        ):
            BaseORM.metadata.create_all(
                sync_conn.engine
            )

    async with async_engine.connect() as conn:
        await conn.run_sync(
            create_tables_if_not_exist
        )
