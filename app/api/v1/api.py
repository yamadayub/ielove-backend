from fastapi import APIRouter
from app.api.v1.endpoints import (
    property_endpoints,
    room_endpoints,
    product_endpoints,
    image_endpoints,
    user_endpoints
)

api_router = APIRouter()

# 各エンドポイントのルーターを登録
api_router.include_router(property_endpoints.router)
api_router.include_router(room_endpoints.router)
api_router.include_router(product_endpoints.router)
api_router.include_router(image_endpoints.router)
api_router.include_router(user_endpoints.router)
