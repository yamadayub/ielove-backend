from fastapi import APIRouter
from app.api.v1.endpoints import (
    product_endpoints,
    property_endpoints,
    room_endpoints,
    image_endpoints,
    user_endpoints,
    company_endpoints,
    spec_endpoints,
    dimension_endpoints,
    seller_endpoints,
    listing_endpoints,
    constants_endpoints,
    transaction_endpoints,
    product_category_endpoints,
    drawing_endpoints
)

api_router = APIRouter()

# 各エンドポイントのルーターを登録
api_router.include_router(property_endpoints.router)
api_router.include_router(room_endpoints.router)
api_router.include_router(product_endpoints.router)
api_router.include_router(image_endpoints.router)
api_router.include_router(user_endpoints.router)
api_router.include_router(company_endpoints.router)
api_router.include_router(spec_endpoints.router)
api_router.include_router(dimension_endpoints.router)
api_router.include_router(seller_endpoints.router)
api_router.include_router(listing_endpoints.router)
api_router.include_router(constants_endpoints.router)
api_router.include_router(transaction_endpoints.router)
api_router.include_router(product_category_endpoints.router)
api_router.include_router(drawing_endpoints.router)
