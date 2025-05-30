from app.routes import LoggingRoute
from fastapi import APIRouter

router = APIRouter(prefix="/items", route_class=LoggingRoute)


@router.get("/")
async def list_items():
    return [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]


@router.get("/{item_id}")
async def read_item(item_id: int):
    return {"id": item_id, "name": f"item-{item_id}"}
