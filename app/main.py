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
        rooms=[RoomSchema(**room.__dict__) for room in rooms],
        products=[ProductSchema(**product.__dict__) for product in products],
        product_specifications=[ProductSpecificationSchema(**spec.__dict__) for spec in product_specifications],
        product_dimensions=[ProductDimensionSchema(**dimension.__dict__) for dimension in product_dimensions],
        images=[ImageSchema(**image.__dict__) for image in images]
    )