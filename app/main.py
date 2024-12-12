
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Property, Room, Product, ProductSpecification, ProductDimension, Image
from app.schemas import PropertySchema, RoomSchema, ProductSchema, ImageSchema

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/properties/{property_id}", response_model=PropertySchema)
async def get_property_details(property_id: int, db: Session = Depends(get_db)):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@app.post("/properties", response_model=dict)
async def create_property(property_data: PropertySchema, db: Session = Depends(get_db)):
    # Create property
    new_property = Property(
        user_id=property_data.user_id,
        name=property_data.name,
        description=property_data.description,
        property_type=property_data.property_type,
        prefecture=property_data.prefecture,
        layout=property_data.layout,
        construction_year=property_data.construction_year,
        construction_month=property_data.construction_month,
        site_area=property_data.site_area,
        building_area=property_data.building_area,
        floor_count=property_data.floor_count,
        structure=property_data.structure,
        design_company_id=property_data.design_company_id,
        construction_company_id=property_data.construction_company_id
    )
    db.add(new_property)
    db.flush()

    # Create property images
    if property_data.images:
        for image_data in property_data.images:
            image = Image(
                url=image_data.url,
                description=image_data.description,
                image_type=image_data.image_type,
                property_id=new_property.id
            )
            db.add(image)
        db.flush()

    # Create rooms with nested products and images
    if property_data.rooms:
        for room_data in property_data.rooms:
            room = Room(
                property_id=new_property.id,
                name=room_data.name,
                description=room_data.description
            )
            db.add(room)
            db.flush()

            # Create room images
            if room_data.images:
                for image_data in room_data.images:
                    image = Image(
                        url=image_data.url,
                        description=image_data.description,
                        image_type=image_data.image_type,
                        property_id=new_property.id,
                        room_id=room.id
                    )
                    db.add(image)
                db.flush()

            # Create products with nested specifications, dimensions and images
            if room_data.products:
                for product_data in room_data.products:
                    product = Product(
                        property_id=new_property.id,
                        room_id=room.id,
                        product_category_id=product_data.product_category_id,
                        manufacturer_id=product_data.manufacturer_id,
                        name=product_data.name,
                        model_number=product_data.model_number,
                        description=product_data.description,
                        catalog_url=product_data.catalog_url
                    )
                    db.add(product)
                    db.flush()

                    # Create product specifications
                    if product_data.specifications:
                        for spec_data in product_data.specifications:
                            spec = ProductSpecification(
                                product_id=product.id,
                                spec_type=spec_data.spec_type,
                                spec_value=spec_data.spec_value,
                                manufacturer_id=spec_data.manufacturer_id,
                                model_number=spec_data.model_number
                            )
                            db.add(spec)
                        db.flush()

                    # Create product dimensions
                    if product_data.dimensions:
                        for dim_data in product_data.dimensions:
                            dimension = ProductDimension(
                                product_id=product.id,
                                dimension_type=dim_data.dimension_type,
                                value=dim_data.value,
                                unit=dim_data.unit
                            )
                            db.add(dimension)
                        db.flush()

                    # Create product images
                    if product_data.images:
                        for image_data in product_data.images:
                            image = Image(
                                url=image_data.url,
                                description=image_data.description,
                                image_type=image_data.image_type,
                                property_id=new_property.id,
                                room_id=room.id,
                                product_id=product.id
                            )
                            db.add(image)
                        db.flush()

    try:
        db.commit()
        return {"property_id": new_property.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
