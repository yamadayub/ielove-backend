from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Property, Room, Product, ProductSpecification, ProductDimension, Image
from app.schemas import PropertySchema  # 追加

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

    rooms = db.query(Room).filter(Room.property_id == property_id).all()
    products = db.query(Product).filter(Product.property_id == property_id).all()
    product_specifications = db.query(ProductSpecification).filter(ProductSpecification.property_id == property_id).all()
    product_dimensions = db.query(ProductDimension).filter(ProductDimension.property_id == property_id).all()
    images = db.query(Image).filter(Image.property_id == property_id).all()

    return PropertySchema(
        id=property.id,
        user_id=property.user_id,
        name=property.name,
        description=property.description,
        property_type=property.property_type,
        prefecture=property.prefecture,
        layout=property.layout,
        construction_year=property.construction_year,
        construction_month=property.construction_month,
        site_area=property.site_area,
        building_area=property.building_area,
        floor_count=property.floor_count,
        structure=property.structure,
        design_company_id=property.design_company_id,
        construction_company_id=property.construction_company_id,
        rooms=[RoomSchema(**room.__dict__) for room in rooms],
        products=[ProductSchema(**product.__dict__) for product in products],
        product_specifications=[ProductSpecificationSchema(**spec.__dict__) for spec in product_specifications],
        product_dimensions=[ProductDimensionSchema(**dimension.__dict__) for dimension in product_dimensions],
        images=[ImageSchema(**image.__dict__) for image in images]
    )

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

    # Create rooms
    if property_data.rooms:
        for room_data in property_data.rooms:
            room = Room(
                property_id=new_property.id,
                name=room_data.name,
                description=room_data.description
            )
            db.add(room)
            db.flush()

    # Create products
    if property_data.products:
        for product_data in property_data.products:
            product = Product(
                property_id=new_property.id,
                room_id=product_data.room_id,
                product_category_id=product_data.product_category_id,
                manufacturer_id=product_data.manufacturer_id,
                name=product_data.name,
                model_number=product_data.model_number,
                description=product_data.description,
                catalog_url=product_data.catalog_url
            )
            db.add(product)
            db.flush()

    # Create images
    if property_data.images:
        for image_data in property_data.images:
            image = Image(
                url=image_data.url,
                description=image_data.description,
                image_type=image_data.image_type,
                property_id=new_property.id,
                room_id=image_data.room_id,
                product_id=image_data.product_id
            )
            db.add(image)

    try:
        db.commit()
        return {"property_id": new_property.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))