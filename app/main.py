from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.property_service import property_service
from app.schemas import (
    PropertyDetailSchema,
    PropertyCreateSchema,
    PropertyCreateBaseSchema,
    PropertySchema
)
from app.services.image_service import image_service
from typing import Optional
from dotenv import load_dotenv
# import os

load_dotenv()  # ENVファイルからの環境変数読み込み
# print("DATABASE_URL in main.py:", os.getenv("DATABASE_URL"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 開発環境
        "http://localhost:5174",  # 追加: フロントエンドの新しいオリジン
        "https://ielove-frontend-staging-4f3b275ce8ee.herokuapp.com/"  # ステージング環境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/properties/{property_id}/details",
         response_model=PropertyDetailSchema)
def get_property_details(
        property_id: int, db: Session = Depends(get_db)) -> PropertyDetailSchema:
    details = property_service.get_property_details(db, property_id)
    if not details:
        raise HTTPException(status_code=404, detail="Property not found")

@app.post("/api/properties/base", response_model=PropertySchema)
def create_property_base(property_data: PropertyCreateBaseSchema,
                        db: Session = Depends(get_db)):
    """物件の基本情報のみを作成する"""
    return property_service.create_property_base(db, property_data)


    return details


@app.post("/api/properties", response_model=int)
def create_property(property_data: PropertyCreateSchema,
                    db: Session = Depends(get_db)):
    return property_service.create_property(db, property_data)


@app.post("/api/images/presigned-url")
def get_presigned_url(file_name: str, content_type: str, db: Session = Depends(get_db)):
    try:
        return image_service.get_upload_url(db, file_name, content_type)
    except Exception as e:
        # エラーログの出力
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="リクエスト処理中にエラーが発生しました。")


@app.delete("/api/images/{image_id}")
def delete_image(image_id: str, db: Session = Depends(get_db)):
    return image_service.delete_image(db, image_id)


@app.post("/api/images/{image_id}/complete")
def complete_image_upload(image_id: str,
                          entity_type: Optional[str] = None,
                          entity_id: Optional[int] = None,
                          db: Session = Depends(get_db)):
    return image_service.complete_upload(db, image_id, entity_type, entity_id)
