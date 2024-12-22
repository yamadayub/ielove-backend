from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.property_service import property_service
from app.services.room_service import room_service
from app.services.product_service import product_service
from app.services.product_specification_service import product_specification_service
from app.services.product_dimension_service import product_dimension_service
from app.schemas import (
    PropertyDetailSchema,
    PropertyCreateSchema,
    PropertyCreateBaseSchema,
    PropertySchema,
    RoomSchema,
    ProductSchema,  # この行を追加
    ProductCreate,
    ProductSpecificationSchema,
    ProductDimensionSchema,
    ProductDetailSchema,
    ImageSchema,
    UserSchema,
    SellerProfileSchema,
    UserUpdate,
    SellerProfileUpdate,
    SellerProfileCreate,
    UserCreate,  # importを追加
    PropertyUpdateSchema,
    ProductSpecificationsUpdateSchema,
    ProductDimensionsUpdateSchema
)
from app.services.image_service import image_service
from typing import Optional
from dotenv import load_dotenv
from typing import List, Optional, Literal
from app.services.user_service import user_service
from app.auth.dependencies import get_current_user
from app.config import settings  # 設定ファイルをインポート
# import os

load_dotenv()  # ENVファイルからの環境変数読み込み
# print("DATABASE_URL in main.py:", os.getenv("DATABASE_URL"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 開発環境
        "http://localhost:5174",  # 追加: フロントエンドの新しいオリジン
        "https://ielove-frontend-staging-4f3b275ce8ee.herokuapp.com"  # ステージング環境
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


@app.post("/api/properties", response_model=PropertySchema, summary="物件情報のみを作成する")
def create_property_base(property_data: PropertyCreateBaseSchema,
                         db: Session = Depends(get_db)):
    """物件の基本情報のみを作成する"""
    return property_service.create_property(db, property_data)


@app.post("/api/properties/{property_id}/rooms", response_model=RoomSchema, summary="部屋情報を作成する")
def create_room(
    property_id: int,
    room_data: RoomSchema,
    db: Session = Depends(get_db)
):
    """物件に紐づく部屋情報を作成する"""
    room_data.property_id = property_id
    return room_service.create_room(db, room_data)


@app.post("/api/rooms/{room_id}/products", response_model=ProductCreate, summary="製品情報を作成する")
def create_product(
    room_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """部屋に紐づく製品情報を作成する"""
    product_data.room_id = room_id
    return product_service.create_product(db, product_data)


@app.get("/api/properties/{property_id}/details",
         response_model=PropertyDetailSchema,
         summary="物件全体の情報を取得する")
def get_property_details(
        property_id: int, db: Session = Depends(get_db)) -> PropertyDetailSchema:
    details = property_service.get_property_details(db, property_id)
    if not details:
        raise HTTPException(status_code=404, detail="Property not found")


@app.post("/api/products/{product_id}/specifications", response_model=ProductSpecificationSchema, summary="製品仕様を追加する")
async def create_product_specification(
    product_id: int,
    spec_data: ProductSpecificationSchema,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    製品に新しい仕様情報を追加します。

    Parameters:
    - product_id: 製品ID
    - spec_data: 仕様情報データ
    - clerk_user_id: ClerkのユーザーID（クエリパラメータ）
    """
    return await product_service.create_product_specification(db, product_id, spec_data)


@app.patch("/api/products/specifications/{spec_id}", response_model=ProductSpecificationSchema, summary="製品仕様を更新する")
async def update_product_specification(
    spec_id: int,
    spec_data: ProductSpecificationSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """既存の仕様情報を更新します。"""
    return await product_service.update_product_specification(db, spec_id, spec_data)


@app.delete("/api/products/specifications/{spec_id}", response_model=None, summary="製品仕様を削除する")
async def delete_product_specification(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定された仕様情報を削除します。"""
    return await product_service.delete_product_specification(db, spec_id)


@app.post("/api/products/{product_id}/dimensions", response_model=ProductDimensionSchema, summary="製品寸法を追加する")
async def create_product_dimension(
    product_id: int,
    dimension_data: ProductDimensionSchema,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    製品に新しい寸法情報を追加します。

    Parameters:
    - product_id: 製品ID
    - dimension_data: 寸法情報データ
    - clerk_user_id: ClerkのユーザーID（クエリパラメータ）
    """
    return await product_service.create_product_dimension(db, product_id, dimension_data)


@app.patch("/api/products/dimensions/{dimension_id}", response_model=ProductDimensionSchema, summary="製品寸法を更新する")
async def update_product_dimension(
    dimension_id: int,
    dimension_data: ProductDimensionSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """既存の寸法情報を更新します。"""
    return await product_service.update_product_dimension(db, dimension_id, dimension_data)


@app.delete("/api/products/dimensions/{dimension_id}", response_model=None, summary="製品寸法を削除する")
async def delete_product_dimension(
    dimension_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定された寸法情報を削除します。"""
    return await product_service.delete_product_dimension(db, dimension_id)


@app.post("/api/properties/whole", response_model=int, summary="物件全体の情報を作成する")
def create_property(property_data: PropertyCreateSchema,
                    db: Session = Depends(get_db)):
    return property_service.create_property_whole(db, property_data)


@app.post("/api/images/presigned-url", summary="画像のアップロードURLを取得する")
def get_presigned_url(file_name: str, content_type: str, db: Session = Depends(get_db)):
    try:
        return image_service.get_upload_url(db, file_name, content_type)
    except Exception as e:
        # エラーログの出力
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="リクエスト処理中にエラーが発生しました。")


@app.delete("/api/images/{image_id}", summary="画像を削除する")
def delete_image(image_id: str, db: Session = Depends(get_db)):
    return image_service.delete_image(db, image_id)


@app.post("/api/images/{image_id}/complete", summary="画像のアップロードを完了する")
def complete_image_upload(image_id: str,
                          entity_type: Optional[str] = None,
                          entity_id: Optional[int] = None,
                          db: Session = Depends(get_db)):
    return image_service.complete_upload(db, image_id, entity_type, entity_id)


@app.post("/api/images/{image_id}/complete", summary="画像のアップロードを完了する")
def complete_image_upload(image_id: str,
                          entity_type: Optional[str] = None,
                          entity_id: Optional[int] = None,
                          db: Session = Depends(get_db)):
    return image_service.complete_upload(db, image_id, entity_type, entity_id)


# Properties
@app.get("/api/properties", response_model=List[PropertySchema], summary="物件一覧を取得する")
def get_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    物件一覧を取得
    """
    return property_service.get_properties(db, skip=skip, limit=limit)


@app.get("/api/properties/{property_id}", response_model=PropertySchema, summary="指定されたIDの物件を取得する")
def get_property(property_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDの物件を取得
    """
    property = property_service.get_property(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

# Rooms


# Rooms
@app.get("/api/properties/{property_id}/rooms", response_model=List[RoomSchema], summary="指定された物件の部屋一覧を取得する")
def get_rooms(
    property_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    指定された物件の部屋一覧を取得
    """
    return room_service.get_rooms(db, property_id=property_id, skip=skip, limit=limit)


@app.get("/api/rooms/{room_id}", response_model=RoomSchema, summary="指定されたIDの部屋を取得する")
def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDの部屋を取得
    """
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

# Products


@app.get("/api/products", response_model=List[ProductSchema], summary="製品一覧を取得する")
def get_products(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    特定の部屋に紐づく製品一覧を取得
    """
    return product_service.get_products_by_room(db, room_id=room_id, skip=skip, limit=limit)


@app.get("/api/products/{product_id}", response_model=ProductSchema, summary="指定されたIDの製品を取得する")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDの製品を取得
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Product Details


@app.get("/api/products/{product_id}/details", response_model=ProductDetailSchema, summary="指定されたIDの製品の詳細情報を取得する")
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    """
    製品の詳細情報（仕様・寸法��含む）を取得
    """
    details = product_service.get_product_details(db, product_id)
    if not details:
        raise HTTPException(status_code=404, detail="Product not found")
    return details

# Images


@app.get("/api/images", response_model=List[ImageSchema], summary="指定されたエンティティに紐づく画像一覧を取得する")
def get_images(
    entity_type: Literal["property", "room", "product"],
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    物件、部屋、製品に紐づく画像一覧を取得

    Parameters:
    - entity_type: "property", "room", "product"のいずれか
    - entity_id: 対象のエンティテのID
    """
    return image_service.get_images_by_entity(
        db,
        entity_type=entity_type,
        entity_id=entity_id
    )


@app.get("/api/images/{image_id}", response_model=ImageSchema, summary="指定されたIDの画像を取得する")
def get_image(image_id: str, db: Session = Depends(get_db)):
    """
    指定されたIDの画像を取得
    """
    image = image_service.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# Users


@app.get("/api/users/me", response_model=UserSchema, tags=["users"])
def get_current_user(clerk_user_id: str, db: Session = Depends(get_db)):
    """
    現在のユーザー情報を取得します。
    """
    user = user_service.get_user_by_clerk_id(db, clerk_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/users/me/seller", response_model=SellerProfileSchema, tags=["users"], summary="現在のユーザーの販売者プロフィールを取得する")
def get_seller_profile(user_id: str, db: Session = Depends(get_db)):
    """
    現在のユーザーの販売者プロフィールを取得します。
    """
    profile = user_service.get_seller_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    return profile


@app.patch("/api/users/me", response_model=UserSchema, tags=["users"], summary="ユーザー情報を更新する")
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    ユーザー情報を更新します。
    """
    updated_user = user_service.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@app.patch("/api/users/me/seller", response_model=SellerProfileSchema, tags=["users"], summary="Seller情報を更新する")
def update_seller_profile(
    user_id: str,
    profile_update: SellerProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    販売者プロフィールを更新します。
    """
    updated_profile = user_service.update_seller_profile(
        db, user_id, profile_update)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    return updated_profile


@app.post("/api/users/me/seller", response_model=SellerProfileSchema, tags=["users"], summary="Seller情報を作��する")
def create_seller_profile(
    user_id: str,
    profile_create: SellerProfileCreate,
    db: Session = Depends(get_db)
):
    """
    販売者プロフィールを作成します。
    """
    return user_service.create_seller_profile(db, user_id, profile_create)


@app.post("/api/users", response_model=UserSchema, tags=["users"], summary="ユーザーを作成する")
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    新規ユーザーを作成します。

    Parameters:
    - user_create: ユーザー作成情報
        - id: Firebase Auth のUID
        - email: メールアドレス
        - name: ユーザー名
        - user_type: "individual" または "business"
        - role: ユーザーの役割（デフォルト: "buyer"）
        - is_active: アクティブ状態（デフォルト: true）

    Returns:
    - 作成されたユーザー情報
    """
    return user_service.create_user(db, user_create)


@app.patch("/properties/{property_id}", response_model=PropertySchema)
async def update_property(
    property_id: int,
    property_data: PropertyUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    物件情報を更新します。
    - property_id: 更新する物件のID
    - property_data: 更新するデータ（部分的な更新が可能）
    """
    return await property_service.update_property(db, property_id, property_data)

# Properties
# 既存のエンドポイントはそのままで、以下を追加


@app.delete("/api/properties/{property_id}", response_model=None, summary="物件を削除する")
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの物件を削除します。
    """
    return await property_service.delete_property(db, property_id)

# Rooms
# 既存のエンドポイントに加えて、以下を追加


@app.patch("/api/rooms/{room_id}", response_model=RoomSchema, summary="部屋情報を更新する")
async def update_room(
    room_id: int,
    room_data: RoomSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの部屋情報を更新します。
    """
    return await room_service.update_room(db, room_id, room_data)


@app.delete("/api/rooms/{room_id}", response_model=None, summary="部屋を削除する")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの部屋を削除します。
    """
    return await room_service.delete_room(db, room_id)

# Products
# 既存のエンドポイントに加えて、以下を追加


@app.patch("/api/products/{product_id}", response_model=ProductSchema, summary="製品情報を更新する")
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの製品情報を更新します。
    """
    return await product_service.update_product(db, product_id, product_data)


@app.delete("/api/products/{product_id}", response_model=None, summary="製品を削除する")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの製品を削除します。
    """
    return await product_service.delete_product(db, product_id)


@app.put("/api/products/{product_id}/specifications", response_model=List[ProductSpecificationSchema], summary="製品仕様を一括更新する")
async def update_product_specifications(
    product_id: int,
    specs_data: ProductSpecificationsUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    製品の仕様情報を一括更新します。
    既存の仕様は全て削除され、新しい仕様に置き換えられます。
    """
    return await product_service.update_product_specifications(db, product_id, specs_data.specifications)


@app.put("/api/products/{product_id}/dimensions", response_model=List[ProductDimensionSchema], summary="製品寸法を一括更新する")
async def update_product_dimensions(
    product_id: int,
    dimensions_data: ProductDimensionsUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    製品の寸法情報を一括更新します。
    既存の寸法は全て削除され、新しい寸法に置き換えられます。
    """
    return await product_service.update_product_dimensions(db, product_id, dimensions_data.dimensions)

# Product Specifications


@app.get("/api/products/{product_id}/specifications", response_model=List[ProductSpecificationSchema], summary="製品仕様一覧を取得する")
async def get_product_specifications(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定された製品の仕様情報一覧を取得します。
    """
    return await product_service.get_product_specifications(db, product_id, skip, limit)


@app.get("/api/products/specifications/{spec_id}", response_model=ProductSpecificationSchema, summary="製品仕様を取得する")
async def get_product_specification(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの仕様情報を取得します。
    """
    return await product_service.get_product_specification(db, spec_id)

# Product Dimensions


@app.get("/api/products/{product_id}/dimensions", response_model=List[ProductDimensionSchema], summary="製品寸法一覧を取得する")
async def get_product_dimensions(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定された製品の寸法情報一覧を取得します。
    """
    return await product_service.get_product_dimensions(db, product_id, skip, limit)


@app.get("/api/products/dimensions/{dimension_id}", response_model=ProductDimensionSchema, summary="製品寸法を取得する")
async def get_product_dimension(
    dimension_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定されたIDの寸法情報を取得します。
    """
    return await product_service.get_product_dimension(db, dimension_id)
