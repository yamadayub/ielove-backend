from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models import User, Property
from app.schemas.listing_item_schemas import ListingItem
from app.crud.listing_item import listing_item

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)


@router.post("", response_model=ListingItem)
def create_listing(
    listing: ListingItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """新規出品を作成"""
    if not current_user.seller_profile:
        raise HTTPException(
            status_code=403,
            detail="Seller profile is required to create listings"
        )

    if listing.listing_type == "PROPERTY_SPECS":
        if not listing.property_id:
            raise HTTPException(
                status_code=400,
                detail="property_id is required for property listing"
            )

        # 物件のオーナーシップ確認
        if not listing_item.verify_property_ownership(
            db=db,
            property_id=listing.property_id,
            user_id=current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to list this property"
            )

    return listing_item.create(
        db=db,
        obj_in=listing,
        seller_id=current_user.seller_profile.id
    )


@router.get("", response_model=List[ListingItem])
def get_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """出品一覧を取得"""
    if not current_user.seller_profile:
        raise HTTPException(
            status_code=403,
            detail="Seller profile is required to view listings"
        )
    return listing_item.get_multi_by_seller(
        db=db,
        seller_id=current_user.seller_profile.id,
        skip=skip,
        limit=limit
    )


@router.get("/{listing_id}", response_model=ListingItem)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """出品情報を取得"""
    db_listing = listing_item.get(db=db, id=listing_id)
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if db_listing.seller_id != current_user.seller_profile.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_listing


@router.put("/{listing_id}", response_model=ListingItem)
def update_listing(
    listing_id: int,
    listing_in: ListingItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """出品情報を更新"""
    db_listing = listing_item.get(db=db, id=listing_id)
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if db_listing.seller_id != current_user.seller_profile.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if listing_in.listing_type == "PROPERTY_SPECS" and listing_in.property_id:
        if not listing_item.verify_property_ownership(
            db=db,
            property_id=listing_in.property_id,
            user_id=current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to list this property"
            )

    return listing_item.update(db=db, db_obj=db_listing, obj_in=listing_in)


@router.delete("/{listing_id}", response_model=ListingItem)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """出品情報を削除"""
    db_listing = listing_item.get(db=db, id=listing_id)
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if db_listing.seller_id != current_user.seller_profile.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return listing_item.remove(db=db, id=listing_id)
