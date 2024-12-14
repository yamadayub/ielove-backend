from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.property_service import property_service
from app.schemas import PropertyDetailSchema, PropertyCreateSchema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.get("/api/properties/{property_id}/details", response_model=PropertyDetailSchema)
def get_property_details(property_id: int, db: Session = Depends(get_db)) -> PropertyDetailSchema:
    details = property_service.get_property_details(db, property_id)
    if not details:
        raise HTTPException(status_code=404, detail="Property not found")
    return details

@app.post("/api/properties", response_model=int)
def create_property(property_data: PropertyCreateSchema, db: Session = Depends(get_db)):
    return property_service.create_property(db, property_data)