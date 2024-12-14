
from typing import Optional
from sqlalchemy.orm import Session
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
    PropertySchema,
    RoomSchema,
    ProductSchema,
    ImageSchema,
    ProductSpecificationSchema,
    ProductDimensionSchema
)

class PropertyService:
    def get_property_detail(self, db: Session, property_id: int) -> Optional[PropertyDetailSchema]:
        property_obj = property_crud.get(db, id=property_id)
        if not property_obj:
            return None
            
        user = user_crud.get(db, id=property_obj.user_id)
        design_company = company_crud.get(db, id=property_obj.design_company_id) if property_obj.design_company_id else None
        construction_company = company_crud.get(db, id=property_obj.construction_company_id) if property_obj.construction_company_id else None
        
        # Get rooms with their products
        rooms = room_crud.get_by_property(db, property_id=property_id)
        rooms_data = []
        
        for room in rooms:
            # Get room images
            room_images = image_crud.get_by_room(db, room_id=room.id)
            
            # Get products for this room
            room_products = product_crud.get_multi_by_room(db, room_id=room.id)
            products_data = []
            
            for product in room_products:
                # Get product details
                specs = spec_crud.get_by_product(db, product_id=product.id)
                dims = dim_crud.get_by_product(db, product_id=product.id)
                product_images = image_crud.get_by_product(db, product_id=product.id)
                
                product_data = {
                    **product.__dict__,
                    'specifications': [spec.__dict__ for spec in specs],
                    'dimensions': [dim.__dict__ for dim in dims],
                    'images': [image.__dict__ for image in product_images]
                }
                products_data.append(product_data)
            
            room_data = {
                **room.__dict__,
                'products': products_data,
                'images': [image.__dict__ for image in room_images]
            }
            rooms_data.append(room_data)
        
        # Get property images
        property_images = image_crud.get_by_property(db, property_id=property_id)
        
        property_data = {
            **property_obj.__dict__,
            'user': user.__dict__ if user else None,
            'design_company': design_company.__dict__ if design_company else None,
            'construction_company': construction_company.__dict__ if construction_company else None,
            'rooms': rooms_data,
            'images': [image.__dict__ for image in property_images]
        }
        
        return PropertyDetailSchema(**property_data)

    @staticmethod
    def create_property(db: Session, property_data: PropertyCreateSchema) -> PropertyDetailSchema:
        # Create property
        property_dict = property_data.dict(exclude={'rooms', 'images'})
        db_property = property_crud.create(db, obj_in=PropertySchema(**property_dict))
        
        # Create images
        if property_data.images:
            for image_data in property_data.images:
                image_dict = image_data.dict()
                image_dict['property_id'] = db_property.id
                image_crud.create(db, obj_in=ImageSchema(**image_dict))
        
        # Create rooms and their related entities
        if property_data.rooms:
            for room_data in property_data.rooms:
                room_dict = room_data.dict(exclude={'products', 'images'})
                room_dict['property_id'] = db_property.id
                db_room = room_crud.create(db, obj_in=RoomSchema(**room_dict))
                
                # Create room images
                if room_data.images:
                    for image_data in room_data.images:
                        image_dict = image_data.dict()
                        image_dict['room_id'] = db_room.id
                        image_crud.create(db, obj_in=ImageSchema(**image_dict))
                
                # Create products and their related entities
                if room_data.products:
                    for product_data in room_data.products:
                        product_dict = product_data.dict(exclude={'specifications', 'dimensions', 'images'})
                        product_dict['property_id'] = db_property.id
                        product_dict['room_id'] = db_room.id
                        db_product = product_crud.create(db, obj_in=ProductSchema(**product_dict))
                        
                        # Create product specifications
                        if product_data.specifications:
                            for spec_data in product_data.specifications:
                                spec_dict = spec_data.dict()
                                spec_dict['product_id'] = db_product.id
                                spec_crud.create(db, obj_in=ProductSpecificationSchema(**spec_dict))
                        
                        # Create product dimensions
                        if product_data.dimensions:
                            for dim_data in product_data.dimensions:
                                dim_dict = dim_data.dict()
                                dim_dict['product_id'] = db_product.id
                                dim_crud.create(db, obj_in=ProductDimensionSchema(**dim_dict))
                        
                        # Create product images
                        if product_data.images:
                            for image_data in product_data.images:
                                image_dict = image_data.dict()
                                image_dict['product_id'] = db_product.id
                                image_crud.create(db, obj_in=ImageSchema(**image_dict))
        
        return PropertyDetailSchema.from_orm(db_property)

property_service = PropertyService()
