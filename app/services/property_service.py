@staticmethod
    def get_property_details(db: Session, property_id: int):
        # Get property with basic relationships
        property_obj = property_crud.get(db, id=property_id)
        if not property_obj:
            return None

        # Get user and companies
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
        
        return {
            **property_obj.__dict__,
            'user': user.__dict__ if user else None,
            'design_company': design_company.__dict__ if design_company else None,
            'construction_company': construction_company.__dict__ if construction_company else None,
            'rooms': rooms_data,
            'images': [image.__dict__ for image in property_images]
        }