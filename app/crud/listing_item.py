from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.models import ListingItem, Property
from app.schemas.listing_item_schemas import ListingItem as ListingItemSchema
from .base import CRUDBase


class CRUDListingItem(CRUDBase[ListingItem, ListingItemSchema, ListingItemSchema]):
    def create(self, db: Session, *, obj_in: ListingItemSchema, seller_id: int) -> ListingItem:
        obj_data = obj_in.model_dump(exclude={'seller_id', 'status'})
        db_obj = ListingItem(
            **obj_data,
            seller_id=seller_id,
            status="DRAFT"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_seller(
        self,
        db: Session,
        *,
        seller_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ListingItem]:
        return (
            db.query(self.model)
            .filter(ListingItem.seller_id == seller_id)
            .order_by(desc(ListingItem.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def verify_property_ownership(self, db: Session, property_id: int, user_id: int) -> bool:
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.user_id == user_id
        ).first()
        return property is not None


listing_item = CRUDListingItem(ListingItem)
