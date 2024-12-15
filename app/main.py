from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.property_service import property_service
from app.services.room_service import room_service
from app.services.product_service import product_service
from app.services.product_specification_service import product_specification_service
from app.schemas import (
    PropertyDetailSchema,
    PropertyCreateSchema,
    PropertyCreateBaseSchema,
    PropertySchema,
    RoomSchema,
    ProductCreate,
    ProductSpecificationSchema
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

@app.post("/api/properties", response_model=PropertySchema)
def create_property_base(property_data: PropertyCreateBaseSchema,
                        db: Session = Depends(get_db)):
    """物件の基本情報のみを作成する"""
    return property_service.create_property(db, property_data)


@app.post("/api/properties/whole", response_model=int)
def create_property(property_data: PropertyCreateSchema,
                    db: Session = Depends(get_db)):
    return property_service.create_property_whole(db, property_data)


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

@app.post("/api/properties/{property_id}/rooms", response_model=RoomSchema)
def create_room(
    property_id: int,
    room_data: RoomSchema,
    db: Session = Depends(get_db)
):
    """物件に紐づく部屋情報を作成する"""
    room_data.property_id = property_id
    return room_service.create_room(db, room_data)


@app.post("/api/images/{image_id}/complete")
@app.post("/api/rooms/{room_id}/products", response_model=ProductCreate)
def create_product(
    room_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """部屋に紐づく製品情報を作成する"""
    product_data.room_id = room_id
    return product_service.create_product(db, product_data)

@app.post("/api/images/{image_id}/complete")
def complete_image_upload(image_id: str,
                          entity_type: Optional[str] = None,
                          entity_id: Optional[int] = None,
                          db: Session = Depends(get_db)):
    return image_service.complete_upload(db, image_id, entity_type, entity_id)

@app.post("/api/products/{product_id}/specifications", response_model=ProductSpecificationSchema)
def create_product_specification(
    product_id: int,
    spec_data: ProductSpecificationSchema,
    db: Session = Depends(get_db)
):
    """製品に紐づく仕様情報を作成する"""
    spec_data.product_id = product_id
    return product_specification_service.create_product_specification(db, spec_data)
