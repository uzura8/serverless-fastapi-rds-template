from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def index():
    return {'message': 'This is content-api'}


@router.get('/{path:path}')
async def any_path(path: str):
    return {'message': f'Here: /{path}'}
