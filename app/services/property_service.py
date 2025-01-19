from typing import Optional, List, Literal, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models import Property, Room, Product, ProductSpecification, ProductDimension, ProductCategory
from app.crud.property import property as property_crud
from app.crud.room import room as room_crud
from app.crud.product import product as product_crud
from app.crud.product_specification import product_specification as spec_crud
from app.crud.product_dimension import product_dimension as dim_crud
from app.crud.image import image as image_crud
from app.crud.user import user as user_crud
from app.crud.company import company as company_crud
from app.crud.product_category import product_category as category_crud
from app.schemas import (
    PropertySchema,
    RoomSchema,
    ProductSchema,
    ImageSchema,
    ProductSpecificationSchema,
    ProductDimensionSchema
)
from fastapi import HTTPException
from fastapi import status


class PropertyService:
    def create_property(self, db: Session, property_data: PropertySchema) -> Property:
        """物件の基本情報と標準的な部屋、デフォルトの製品を作成する"""
        # 物件の基本情報を作成（独立したトランザクション）
        try:
            property_dict = property_data.model_dump()
            db_property = property_crud.create(
                db, obj_in=PropertySchema(**property_dict))
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

        # デフォルトの部屋を作成
        default_rooms = [
            "リビングダイニング",
            "キッチン",
            "寝室",
            "トイレ",
            "洗面室・浴室",
            "玄関",
            "廊下"
        ]

        # 部屋タイプごとのデフォルトプロダクトカテゴリID
        room_product_categories = {
            # 基本設備 + 窓 + ダイニングセット + ソファ
            "リビングダイニング": [1, 2, 3, 4, 5, 6, 9, 10, 11],
            "キッチン": [1, 2, 3, 4, 5, 7, 8],  # 基本設備 + キッチン + カップボード
            "寝室": [1, 2, 3, 4, 5, 6, 12],  # 基本設備 + 窓 + ベッド
            "トイレ": [1, 2, 3, 4, 5],  # 基本設備のみ
            "洗面室・浴室": [1, 2, 3, 4, 5, 14],  # 基本設備のみ + バス
            "玄関": [1, 2, 3, 4, 5],  # 基本設備のみ
            "廊下": [1, 2, 3, 4, 5]   # 基本設備のみ
        }

        # プロダクトカテゴリを取得
        all_categories = db.query(ProductCategory).all()
        category_dict = {cat.id: cat.name for cat in all_categories}

        # 各部屋を作成（部屋ごとに独立したトランザクション）
        for room_name in default_rooms:
            try:
                room_data = RoomSchema(
                    name=room_name,
                    property_id=db_property.id,
                    description=f"{room_name}の説明"
                )
                db_room = room_crud.create(db, obj_in=room_data)
                db.commit()

                # その部屋の製品を作成（製品ごとに独立したトランザクション）
                category_ids = room_product_categories.get(
                    room_name, [1, 2, 3, 4, 5])
                for category_id in category_ids:
                    if category_id in category_dict:
                        try:
                            product_data = ProductSchema(
                                name=category_dict[category_id],
                                room_id=db_room.id,
                                product_category_id=category_id,
                                description=f"{category_dict[category_id]}の説明"
                            )
                            product_crud.create(db, obj_in=product_data)
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            continue

            except Exception as e:
                db.rollback()
                continue

        return db_property

    def get_properties(self, db: Session, skip: int = 0, limit: int = 100) -> List[Property]:
        """
        物件一覧を取得する

        Args:
            db (Session): データベースセッション
            skip (int): スキップする件数
            limit (int): 取得する最大件数

        Returns:
            List[Property]: 物件のリスト
        """
        return property_crud.get_multi(db, skip=skip, limit=limit)

    def get_property(self, db: Session, property_id: int) -> Optional[Property]:
        """
        指定されたIDの物件を取得する

        Args:
            db (Session): データベースセッション
            property_id (int): 物件ID

        Returns:
            Optional[Property]: 物件オブジェクト。存在しない場合はNone
        """
        return property_crud.get(db, id=property_id)

    def get_property_details(self, db: Session, property_id: int):
        """物件の詳細情報を関連データと共に取得"""

        # 物件情報を関連データと共に取得
        property = db.query(Property)\
            .options(
                joinedload(Property.rooms)
                .joinedload(Room.products)
                .joinedload(Product.specifications),
                joinedload(Property.rooms)
                .joinedload(Room.products)
                .joinedload(Product.dimensions)
        )\
            .filter(Property.id == property_id)\
            .first()

        if not property:
            raise HTTPException(status_code=404, detail="Property not found")

        # 画像情報を取得
        property_images = image_crud.get_images(db, property_id=property_id)

        # レスポンスの構築
        result = {
            "id": property.id,
            "user_id": property.user_id,
            "name": property.name,
            "description": property.description,
            "property_type": property.property_type,
            "prefecture": property.prefecture,
            "layout": property.layout,
            "construction_year": property.construction_year,
            "construction_month": property.construction_month,
            "site_area": property.site_area,
            "building_area": property.building_area,
            "floor_count": property.floor_count,
            "structure": property.structure,
            "design_company": property.design_company,
            "construction_company": property.construction_company,
            "created_at": property.created_at,
            "updated_at": property.updated_at,
            "status": property.status,
            "images": property_images,
            "rooms": []
        }

        for room in property.rooms:
            # 部屋の画像を取得
            room_images = image_crud.get_images(db, room_id=room.id)

            room_data = {
                "id": room.id,
                "name": room.name,
                "description": room.description,
                "property_id": room.property_id,
                "created_at": room.created_at,
                "updated_at": room.updated_at,
                "status": room.status,
                "images": room_images,
                "products": []
            }

            for product in room.products:
                # 製品の画像を取得
                product_images = image_crud.get_images(
                    db, product_id=product.id)

                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "room_id": product.room_id,
                    "product_category_id": product.product_category_id,
                    "manufacturer_id": product.manufacturer_id,
                    "product_code": product.product_code,
                    "catalog_url": product.catalog_url,
                    "created_at": product.created_at,
                    "updated_at": product.updated_at,
                    "status": product.status,
                    "images": product_images,
                    "specifications": product.specifications,
                    "dimensions": product.dimensions
                }
                room_data["products"].append(product_data)

            result["rooms"].append(room_data)

        return result

    @staticmethod
    def create_property_whole(db: Session, property_data: PropertySchema) -> int:
        try:
            # Create property record
            property_dict = property_data.model_dump(
                exclude={'rooms', 'images'})
            db_property = property_crud.create(
                db, obj_in=PropertySchema(**property_dict))

            # Create property images
            if property_data.images:
                for image_data in property_data.images:
                    image_dict = image_data.model_dump()
                    image_dict['property_id'] = db_property.id
                    image_dict['room_id'] = None
                    image_dict['product_id'] = None
                    image_crud.create(db, obj_in=ImageSchema(**image_dict))

            # Create rooms and their related entities
            if property_data.rooms:
                for room_data in property_data.rooms:
                    # Create room record
                    room_dict = room_data.model_dump(
                        exclude={'products', 'images'})
                    room_dict['property_id'] = db_property.id
                    db_room = room_crud.create(
                        db, obj_in=RoomSchema(**room_dict))

                    # Create room images
                    if room_data.images:
                        for image_data in room_data.images:
                            image_dict = image_data.model_dump()
                            image_dict['property_id'] = None
                            image_dict['room_id'] = db_room.id
                            image_dict['product_id'] = None
                            image_crud.create(
                                db, obj_in=ImageSchema(**image_dict))

                    # Create products and their related entities
                    if room_data.products:
                        for product_data in room_data.products:
                            # Create product record
                            product_dict = product_data.model_dump(
                                exclude={'specifications', 'dimensions', 'images'})
                            product_dict['property_id'] = db_property.id
                            product_dict['room_id'] = db_room.id
                            db_product = product_crud.create(
                                db, obj_in=ProductSchema(**product_dict))

                            # Create product images
                            if product_data.images:
                                for image_data in product_data.images:
                                    image_dict = image_data.model_dump()
                                    image_dict['property_id'] = None
                                    image_dict['room_id'] = None
                                    image_dict['product_id'] = db_product.id
                                    image_crud.create(
                                        db, obj_in=ImageSchema(**image_dict))

                            # Create product specifications
                            if product_data.specifications:
                                for spec_data in product_data.specifications:
                                    spec_dict = spec_data.model_dump()
                                    spec_dict['product_id'] = db_product.id
                                    spec_crud.create(
                                        db, obj_in=ProductSpecificationSchema(**spec_dict))

                            # Create product dimensions
                            if product_data.dimensions:
                                for dim_data in product_data.dimensions:
                                    dim_dict = dim_data.model_dump()
                                    dim_dict['product_id'] = db_product.id
                                    dim_crud.create(
                                        db, obj_in=ProductDimensionSchema(**dim_dict))

            db.refresh(db_property)
            return db_property.id

        except Exception as e:
            db.rollback()
            raise e

    async def update_property(self, db: Session, property_id: int, property_data: PropertySchema):
        db_property = db.query(Property).filter(
            Property.id == property_id).first()

        if not db_property:
            raise HTTPException(status_code=404, detail="Property not found")

        # 更新可能なフィールドのみを取得
        update_data = property_data.model_dump(exclude_unset=True)

        # company_idフィールドの処理は不要になりました

        for field, value in update_data.items():
            setattr(db_property, field, value)

        try:
            db.commit()
            db.refresh(db_property)
            return db_property
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_property(self, db: Session, property_id: int):
        db_property = db.query(Property).filter(
            Property.id == property_id).first()

        if not db_property:
            raise HTTPException(status_code=404, detail="Property not found")

        try:
            # 論理削除を実装
            from datetime import datetime
            db_property.is_deleted = True
            db_property.deleted_at = datetime.now()
            db.commit()
            db.refresh(db_property)
            return {"message": "Property deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def get_properties_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        filters: Dict[str, Any] = None
    ) -> Tuple[List[Property], int]:
        """
        指定されたユーザーIDの物件一覧を取得する

        Args:
            db: データベースセッション
            user_id: ユーザーID
            skip: スキップする件数
            limit: 取得する最大件数
            filters: フィルター条件

        Returns:
            Tuple[List[Property], int]: 物件リストと総件数のタプル
        """
        # 論理削除されていない物件のみを取得するようにフィルターを追加
        if filters is None:
            filters = {}
        filters['is_deleted'] = False
        return property_crud.get_by_user_with_filters(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            filters=filters
        )

    def is_my_property(self, db: Session, property_id: int, user_id: int) -> bool:
        """
        指定された物件が現在のユーザーのものかを確認する

        Args:
            db (Session): データベースセッション
            property_id (int): 物件ID
            user_id (int): ユーザーID

        Returns:
            bool: ユーザーの物件である場合はTrue、そうでない場合はFalse
        """
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.user_id == user_id,
            Property.is_deleted == False
        ).first()
        return property is not None


property_service = PropertyService()
