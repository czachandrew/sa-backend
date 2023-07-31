from fastapi import APIRouter

from .route_items import router as items_router
from .route_users import router as users_router
from .auth import router as auth_router
from .route_orders import router as orders_router

api_router = APIRouter()
api_router.include_router(items_router, prefix="/items", tags=["items"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
