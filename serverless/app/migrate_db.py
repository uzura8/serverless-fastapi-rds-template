import asyncio

from app.db import async_engine
from app.models.task import Base


async def reset_database() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())
