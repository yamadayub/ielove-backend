
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Room
from app.schemas import PropertySchema
from app.crud import ImageCRUD, ProductCRUD, ProductSpecificationCRUD, ProductDimensionCRUD
from app.crud.property import PropertyCRUD

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/properties/{property_id}", response_model=PropertySchema)
async def get_property_details(property_id: int, db: Session = Depends(get_db)):
    property = PropertyCRUD.get(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@app.post("/properties", response_model=PropertySchema)
async def create_property(property_data: PropertySchema, db: Session = Depends(get_db)):
    try:
        # Create property using PropertyCRUD
        new_property = PropertyCRUD.create(db, property_data)

        # Create property images using ImageCRUD
        if property_data.images:
            for image_data in property_data.images:
                image_data.property_id = new_property.id
                ImageCRUD.create(db, image_data)

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

                if room_data.images:
                    for image_data in room_data.images:
                        image_data.property_id = new_property.id
                        image_data.room_id = room.id
                        ImageCRUD.create(db, image_data)

                if room_data.products:
                    for product_data in room_data.products:
                        product_data.property_id = new_property.id
                        product_data.room_id = room.id
                        product = ProductCRUD.create(db, product_data)

                        if product_data.specifications:
                            for spec_data in product_data.specifications:
                                spec_data.product_id = product.id
                                ProductSpecificationCRUD.create(db, spec_data)

                        if product_data.dimensions:
                            for dim_data in product_data.dimensions:
                                dim_data.product_id = product.id
                                ProductDimensionCRUD.create(db, dim_data)

                        if product_data.images:
                            for image_data in product_data.images:
                                image_data.property_id = new_property.id
                                image_data.room_id = room.id
                                image_data.product_id = product.id
                                ImageCRUD.create(db, image_data)

        db.commit()
        return new_property
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
