
from sqlalchemy.orm import Session
from app.models import Property
from app.schemas import PropertySchema

class PropertyCRUD:
    @staticmethod
    def create(db: Session, property_data: PropertySchema) -> Property:
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
        return new_property

    @staticmethod
    def get(db: Session, property_id: int) -> Property:
        return db.query(Property).filter(Property.id == property_id).first()
