
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Property
from app.crud.property import property as property_crud
from app.crud.room import room as room_crud
from app.crud.product import product as product_crud
from app.crud.product_specification import product_specification as spec_crud
from app.crud.product_dimension import product_dimension as dim_crud
from app.crud.image import image as image_crud
from app.crud.user import user as user_crud
from app.crud.company import company as company_crud
from app.schemas import (
    PropertyDetailSchema,
    PropertyCreateSchema,
    PropertyCreateBaseSchema,
    PropertySchema,
    RoomSchema,
    ProductSchema,
    ImageSchema,
    ProductSpecificationSchema,
    ProductDimensionSchema
)

class PropertyService:
    def create_property_base(self, db: Session, property_data: PropertyCreateBaseSchema) -> Property:
        """物件の基本情報のみを作成する"""
        return property_crud.create(db, obj_in=property_data)

    def get_property_details(self, db: Session, property_id: int) -> Optional[PropertyDetailSchema]:
        property_obj = property_crud.get(db, id=property_id)
        if not property_obj:
            return None
            
        # Create a dictionary with property data and relationships
        property_data = {
            "id": property_obj.id,
            "user_id": property_obj.user_id,
            "name": property_obj.name,
            "description": property_obj.description,
            "property_type": property_obj.property_type,
            "prefecture": property_obj.prefecture,
            "layout": property_obj.layout,
            "construction_year": property_obj.construction_year,
            "construction_month": property_obj.construction_month,
            "site_area": property_obj.site_area,
            "building_area": property_obj.building_area,
            "floor_count": property_obj.floor_count,
            "structure": property_obj.structure,
            "design_company_id": property_obj.design_company_id,
            "construction_company_id": property_obj.construction_company_id,
            "user": {
                "id": property_obj.user.id,
                "email": property_obj.user.email,
                "name": property_obj.user.name,
                "user_type": property_obj.user.user_type,
                "role": property_obj.user.role
            } if property_obj.user else None,
            "design_company": {
                "id": property_obj.design_company.id,
                "name": property_obj.design_company.name,
                "company_type": property_obj.design_company.company_type,
                "description": property_obj.design_company.description,
                "website": property_obj.design_company.website
            } if property_obj.design_company else None,
            "construction_company": {
                "id": property_obj.construction_company.id,
                "name": property_obj.construction_company.name,
                "company_type": property_obj.construction_company.company_type,
                "description": property_obj.construction_company.description,
                "website": property_obj.construction_company.website
            } if property_obj.construction_company else None,
            "rooms": [{
                "id": room.id,
                "property_id": room.property_id,
                "name": room.name,
                "description": room.description,
                "products": [{
                    "id": product.id,
                    "property_id": product.property_id,
                    "room_id": product.room_id,
                    "product_category_id": product.product_category_id,
                    "manufacturer_id": product.manufacturer_id,
                    "name": product.name,
                    "product_code": product.product_code,
                    "description": product.description,
                    "catalog_url": product.catalog_url,
                    "specifications": [{
                        "id": spec.id,
                        "product_id": spec.product_id,
                        "spec_type": spec.spec_type,
                        "spec_value": spec.spec_value,
                        "manufacturer_id": spec.manufacturer_id,
                        "model_number": spec.model_number
                    } for spec in product.specifications],
                    "dimensions": [{
                        "id": dim.id,
                        "product_id": dim.product_id,
                        "dimension_type": dim.dimension_type,
                        "value": dim.value,
                        "unit": dim.unit
                    } for dim in product.dimensions],
                    "images": [{
                        "id": image.id,
                        "url": image.url,
                        "description": image.description,
                        "image_type": image.image_type,
                        "property_id": image.property_id,
                        "room_id": image.room_id,
                        "product_id": image.product_id
                    } for image in product.images]
                } for product in room.products],
                "images": [{
                    "id": image.id,
                    "url": image.url,
                    "description": image.description,
                    "image_type": image.image_type,
                    "property_id": image.property_id,
                    "room_id": image.room_id,
                    "product_id": image.product_id
                } for image in room.images]
            } for room in property_obj.rooms] if property_obj.rooms else [],
            "images": [{
                "id": image.id,
                "url": image.url,
                "description": image.description,
                "image_type": image.image_type,
                "property_id": image.property_id,
                "room_id": image.room_id,
                "product_id": image.product_id
            } for image in property_obj.images] if property_obj.images else []
        }
        
        return PropertyDetailSchema.model_validate(property_data)

    @staticmethod
    def create_property(db: Session, property_data: PropertyCreateSchema) -> int:
        try:
            # Create property record
            property_dict = property_data.model_dump(exclude={'rooms', 'images'})
            db_property = property_crud.create(db, obj_in=PropertySchema(**property_dict))

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
                    room_dict = room_data.model_dump(exclude={'products', 'images'})
                    room_dict['property_id'] = db_property.id
                    db_room = room_crud.create(db, obj_in=RoomSchema(**room_dict))

                    # Create room images
                    if room_data.images:
                        for image_data in room_data.images:
                            image_dict = image_data.model_dump()
                            image_dict['property_id'] = None
                            image_dict['room_id'] = db_room.id
                            image_dict['product_id'] = None
                            image_crud.create(db, obj_in=ImageSchema(**image_dict))

                    # Create products and their related entities
                    if room_data.products:
                        for product_data in room_data.products:
                            # Create product record
                            product_dict = product_data.model_dump(exclude={'specifications', 'dimensions', 'images'})
                            product_dict['property_id'] = db_property.id
                            product_dict['room_id'] = db_room.id
                            db_product = product_crud.create(db, obj_in=ProductSchema(**product_dict))

                            # Create product images
                            if product_data.images:
                                for image_data in product_data.images:
                                    image_dict = image_data.model_dump()
                                    image_dict['property_id'] = None
                                    image_dict['room_id'] = None
                                    image_dict['product_id'] = db_product.id
                                    image_crud.create(db, obj_in=ImageSchema(**image_dict))

                            # Create product specifications
                            if product_data.specifications:
                                for spec_data in product_data.specifications:
                                    spec_dict = spec_data.model_dump()
                                    spec_dict['product_id'] = db_product.id
                                    spec_crud.create(db, obj_in=ProductSpecificationSchema(**spec_dict))

                            # Create product dimensions
                            if product_data.dimensions:
                                for dim_data in product_data.dimensions:
                                    dim_dict = dim_data.model_dump()
                                    dim_dict['product_id'] = db_product.id
                                    dim_crud.create(db, obj_in=ProductDimensionSchema(**dim_dict))

            db.refresh(db_property)
            return db_property.id

        except Exception as e:
            db.rollback()
            raise e

property_service = PropertyService()
