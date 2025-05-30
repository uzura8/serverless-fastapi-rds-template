from fastapi import APIRouter
# from fastapi.security import APIKeyHeader

from .tasks.views import router as task_router


# async def get_api_key(
#     api_key_header: str = Security(APIKeyHeader(
#         name='APP-API-KEY', auto_error=True)),
# ) -> str:
#     if api_key_header != 'DUMMY-KEY':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
#     return api_key_header
# router = APIRouter(dependencies=[Depends(get_api_key)])
router = APIRouter()
router.include_router(task_router)
