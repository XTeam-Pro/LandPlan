"""Lands API routes"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.bounded_contexts.lands.service import LandsService
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.land import (
    LandCreate,
    LandUpdate,
    UserLandCreate,
    LandListResponse,
    LandDetailResponse,
    LandFeatureSchema,
    LandsFilterRequest,
)

router = APIRouter(prefix="/api/v1/lands", tags=["Lands"])


@router.get(
    "",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Search and filter lands",
    description="Get list of land parcels with filtering and pagination",
)
async def list_lands(
    region_id: int = Query(None, description="Filter by region ID"),
    city_id: int = Query(None, description="Filter by city ID"),
    price_min: float = Query(None, description="Minimum price"),
    price_max: float = Query(None, description="Maximum price"),
    area_min: float = Query(None, description="Minimum area in sq meters"),
    area_max: float = Query(None, description="Maximum area in sq meters"),
    deal_type: str = Query(None, description="Deal type (purchase, rent, lease)"),
    search_query: str = Query(None, description="Full-text search query"),
    latitude: float = Query(None, description="Center latitude for geo search"),
    longitude: float = Query(None, description="Center longitude for geo search"),
    bbox_radius_km: float = Query(10, description="Search radius in kilometers"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Search and filter land parcels.

    **Query Parameters:**
    - **region_id**: Filter by region
    - **city_id**: Filter by city
    - **price_min/price_max**: Price range filter
    - **deal_type**: Type of deal (purchase, rent, lease)
    - **search_query**: Full-text search in title, description, address
    - **latitude/longitude**: Geo-center for radius search
    - **bbox_radius_km**: Radius for geo search (default: 10km)
    - **page**: Pagination page (default: 1)
    - **limit**: Results per page (default: 20, max: 100)

    **Returns:**
    - List of land parcels matching filters
    - Total count of results
    - Pagination metadata
    """

    filters = LandsFilterRequest(
        region_id=region_id,
        city_id=city_id,
        price_min=price_min,
        price_max=price_max,
        area_min=area_min,
        area_max=area_max,
        deal_type=deal_type,
        search_query=search_query,
        latitude=latitude,
        longitude=longitude,
        bbox_radius_km=bbox_radius_km,
        page=page,
        limit=limit,
    )
    # TODO: add region_name, city_name, listing_type, has_building, land_category, cadastral_number
    # filters when frontend passes them

    lands, total = LandsService.get_lands(db, filters)

    return {
        "items": lands,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get(
    "/{land_id}",
    response_model=LandDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get land details",
    description="Get detailed information about a specific land parcel",
)
async def get_land(land_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a land parcel.

    **Parameters:**
    - **land_id**: ID of the land parcel

    **Returns:**
    - Detailed land parcel information
    - Land features (water, electricity, boundaries, etc.)
    """
    return LandsService.get_land_by_id(db, land_id)


@router.get(
    "/{land_id}/features",
    response_model=LandFeatureSchema,
    status_code=status.HTTP_200_OK,
    summary="Get land features",
    description="Get features and characteristics of a land parcel",
)
async def get_land_features(land_id: int, db: Session = Depends(get_db)):
    """
    Get land features (utilities, boundaries, etc.).

    **Parameters:**
    - **land_id**: ID of the land parcel

    **Returns:**
    - Land features schema with:
      - has_water: Water availability
      - has_electricity: Electricity availability
      - has_gas: Gas availability
      - has_roads: Road access
      - boundaries_defined: Whether boundaries are marked
      - build_ready: Whether ready for construction
    """
    features = LandsService.get_land_features(db, land_id)
    return LandFeatureSchema.from_orm(features)


@router.get(
    "/{land_id}/companies",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get relevant companies for land",
)
async def get_land_companies(land_id: int, db: Session = Depends(get_db)):
    """
    Get relevant companies for a land parcel based on recommendations.

    **Parameters:**
    - **land_id**: ID of the land parcel

    **Returns:**
    - Companies grouped by recommended service
    """
    return LandsService.get_land_companies(db, land_id)


@router.post(
    "",
    response_model=LandDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new land",
    description="Create a new land parcel (admin/import only)",
)
async def create_land(
    land_data: LandCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new land parcel.

    **Note:** This endpoint is typically used for data imports and requires admin privileges.

    **Parameters:**
    - **source_id**: Data source ID
    - **region_id**: Region ID
    - **title**: Land parcel title
    - **address**: Full address
    - **latitude**: Latitude coordinate
    - **longitude**: Longitude coordinate
    - **price**: Price (optional)
    - **area**: Area in square meters (optional)

    **Returns:**
    - Created land parcel with all details
    """
    return LandsService.create_land(db, land_data)


@router.patch(
    "/{land_id}",
    response_model=LandDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update land",
    description="Update land parcel information",
)
async def update_land(
    land_id: int,
    land_data: LandUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a land parcel.

    **Parameters:**
    - **land_id**: ID of land to update
    - **land_data**: Fields to update (all optional)

    **Returns:**
    - Updated land parcel
    """
    return LandsService.update_land(db, land_id, land_data)


@router.post(
    "/user-listing",
    response_model=LandDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user listing (owner/agency)",
    description="Create a land listing by user (owner) or company (agency). Requires cadastral number.",
)
async def create_user_listing(
    listing_data: UserLandCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a land listing by authenticated user.

    - Users get listing_type = 'owner' (от собственника)
    - Companies get listing_type = 'agency' (от агентства)
    - Cadastral number is REQUIRED — without it the listing is rejected
    - New listings go to status 'pending_moderation' until admin approves
    """
    if not listing_data.cadastral_number or not listing_data.cadastral_number.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кадастровый номер обязателен для публикации объявления",
        )

    user_id = current_user["user_id"]
    user_role = current_user["payload"].get("role", "user")
    listing_type = "agency" if user_role == "company" else "owner"

    land_create = LandCreate(
        title=listing_data.title,
        description=listing_data.description,
        address=listing_data.address,
        latitude=listing_data.latitude,
        longitude=listing_data.longitude,
        cadastral_number=listing_data.cadastral_number,
        price=listing_data.price,
        area=listing_data.area,
        land_category=listing_data.land_category,
        allowed_usage=listing_data.allowed_usage,
        deal_type=listing_data.deal_type,
        has_building=listing_data.has_building,
        photos=listing_data.photos or [],
        contact_phone=listing_data.contact_phone,
        listing_type=listing_type,
        region_id=1,  # TODO: resolve from region_name
    )

    land = LandsService.create_land(db, land_create)

    # Set owner and moderation status
    from app.models.land import Land as LandModel
    db_land = db.query(LandModel).get(land.id)
    if db_land:
        db_land.owner_user_id = user_id
        db_land.status = "pending_moderation"
        if listing_data.features:
            from app.models.land import LandFeature
            feature = db.query(LandFeature).filter(LandFeature.land_id == land.id).first()
            if not feature:
                feature = LandFeature(land_id=land.id)
                db.add(feature)
            feature.has_water = listing_data.features.has_water
            feature.has_electricity = listing_data.features.has_electricity
            feature.has_gas = listing_data.features.has_gas
            feature.has_roads = listing_data.features.has_roads
            feature.boundaries_defined = listing_data.features.boundaries_defined
            feature.build_ready = listing_data.features.build_ready
        db.commit()
        db.refresh(db_land)

    return land
