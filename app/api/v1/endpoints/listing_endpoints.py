from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models import User, Property, ListingItem, SellerProfile
from app.schemas.listing_item_schemas import ListingItem as ListingItemSchema
from app.crud.listing_item import listing_item
from app.enums import ListingStatus, Visibility

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)


@router.post("", response_model=ListingItemSchema)
def create_listing(
    listing: ListingItemSchema,
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


@router.get("", response_model=List[ListingItemSchema])
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


@router.get("/my-listings", response_model=List[ListingItemSchema])
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(
        None, description="DRAFT, PUBLISHED, RESERVED, SOLD, CANCELLEDのいずれか")
):
    """
    ログインユーザーの出品一覧を取得する

    Parameters:
    - skip: スキップする件数
    - limit: 取得する最大件数
    - status: フィルタリングするステータス（オプション）
    """
    if not current_user.seller_profile:
        raise HTTPException(
            status_code=403,
            detail="Seller profile is required to view listings"
        )

    query = db.query(ListingItem)\
        .filter(ListingItem.seller_id == current_user.seller_profile.id)

    if status:
        try:
            listing_status = ListingStatus(status)
            query = query.filter(ListingItem.status == listing_status)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status value. Must be one of: {', '.join(ListingStatus.__members__.keys())}"
            )

    # 作成日時の降順でソート
    query = query.order_by(ListingItem.created_at.desc())

    # ページネーション
    total = query.count()
    items = query.offset(skip).limit(limit).all()

    # ヘッダーに総件数を追加
    response = Response()
    response.headers["X-Total-Count"] = str(total)

    return items


@router.get("/{listing_id}", response_model=ListingItemSchema)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """出品情報を取得"""
    db_listing = listing_item.get(db=db, id=listing_id)
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # 自分の物件の場合のみ、非公開でも閲覧可能
    if current_user.seller_profile and db_listing.seller_id == current_user.seller_profile.id:
        return db_listing

    # 他人の物件の場合は、公開されているもののみ閲覧可能
    if db_listing.visibility != Visibility.PUBLIC or db_listing.status != ListingStatus.PUBLISHED:
        raise HTTPException(
            status_code=403, detail="This listing is not public")

    return db_listing


@router.put("/{listing_id}", response_model=ListingItemSchema)
def update_listing(
    listing_id: int,
    listing_in: ListingItemSchema,
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


@router.delete("/{listing_id}", response_model=ListingItemSchema)
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


@router.get("/property/{property_id}", response_model=Dict[str, List[dict]])
async def get_listing_items_by_property(
    property_id: int,
    include_seller: bool = Query(True, description="セラー情報を含めるかどうか"),
    db: Session = Depends(get_db),
):
    """
    指定された物件に紐づく出品一覧を取得します。

    - ステータスがPUBLISHEDのみ
    - visibilityがPUBLICのみ
    - property_idに紐づく全てのListingItem
    """

    # 物件の存在確認
    property_exists = db.query(Property).filter(
        Property.id == property_id).first()
    if not property_exists:
        return {"items": []}

    # クエリの構築
    query = (
        select(ListingItem)
        .options(
            joinedload(ListingItem.property),
            joinedload(ListingItem.seller).joinedload(SellerProfile.user)
        )
        .join(Property)
        .filter(
            ListingItem.property_id == property_id,
            ListingItem.status == ListingStatus.PUBLISHED,
            ListingItem.visibility == Visibility.PUBLIC
        )
        .order_by(ListingItem.created_at.desc())
    )

    # クエリの実行
    listing_items = db.execute(query).unique().scalars().all()

    # レスポンスの構築
    response_items = []
    for item in listing_items:
        response_item = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "price": item.price,
            "listing_type": item.listing_type.value,
            "created_at": item.created_at,
            "property": {
                "id": item.property.id,
                "name": item.property.name
            }
        }

        if include_seller:
            response_item["seller"] = {
                "id": item.seller.id,
                "name": item.seller.user.name
            }
        else:
            response_item["seller"] = None

        response_items.append(response_item)

    return {"items": response_items}
