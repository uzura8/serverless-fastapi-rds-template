from app.api.routers import done, task
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(task.router)
api_router.include_router(done.router)
