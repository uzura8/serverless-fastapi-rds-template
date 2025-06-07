from contextlib import asynccontextmanager
from app.api import router
from app.core.config import settings
from app.exceptions import init_exception_handler
from app.log import init_log
from app.middlewares import init_middlewares
from app.database import create_database_if_not_exist
from fastapi import FastAPI
from mangum import Mangum


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await create_database_if_not_exist()
    yield


app = FastAPI(
    title='FastAPI Sample',
    lifespan=lifespan
)

init_log()
init_exception_handler(app)
init_middlewares(app)
app.include_router(router, prefix=settings.API_V1_STR)
handler = Mangum(app)
