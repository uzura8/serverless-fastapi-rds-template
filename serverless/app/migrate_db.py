import asyncio

from app.database import async_engine
from app.models import BaseORM


async def reset_database() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.drop_all)
        await conn.run_sync(BaseORM.metadata.create_all)
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())
