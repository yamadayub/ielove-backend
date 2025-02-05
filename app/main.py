from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.api import api_router
from app.middleware.logging import log_request_middleware

app = FastAPI(
    title="ieLove API",
    description="不動産物件管理のためのAPI",
    version="1.0.0"
)

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ロギングミドルウェアの追加
app.middleware("http")(log_request_middleware)

# APIルーターの登録
app.include_router(api_router, prefix="/api")
