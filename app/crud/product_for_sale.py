from sqlalchemy.orm import Session
from app.models import ProductForSale
from app.schemas import ProductForSaleSchema
from .base import BaseCRUD

class ProductForSaleCRUD(BaseCRUD[ProductForSale, ProductForSaleSchema, ProductForSaleSchema]):
    def __init__(self):
        super().__init__(ProductForSale)

    def get_by_seller(self, db: Session, seller_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.seller_id == seller_id)\
            .offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.status == status)\
            .offset(skip).limit(limit).all()

    def get_by_sale_type(self, db: Session, sale_type: str, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.sale_type == sale_type)\
            .offset(skip).limit(limit).all()

product_for_sale = ProductForSaleCRUD()