"""Land request/response schemas"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LandFeatureSchema(BaseModel):
    """Land features schema"""

    has_water: bool = False
    has_electricity: bool = False
    has_gas: bool = False
    has_roads: bool = False
    boundaries_defined: bool = False
    build_ready: bool = False
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class LandBase(BaseModel):
    """Base land schema"""

    title: str
    description: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    cadastral_number: Optional[str] = None
    price: Optional[float] = None
    area: Optional[float] = None
    land_category: Optional[str] = None
    allowed_usage: Optional[str] = None
    deal_type: Optional[str] = None
    listing_type: str = "import"
    has_building: bool = False
    photos: List[str] = Field(default_factory=list)
    contact_phone: Optional[str] = None


class LandCreate(LandBase):
    """Land creation schema (admin/import)"""

    source_id: Optional[int] = None
    region_id: int
    city_id: Optional[int] = None
    external_id: Optional[str] = None


class UserLandCreate(BaseModel):
    """Land creation schema for user listings (owner/agency)"""

    cadastral_number: str = Field(..., min_length=3, description="Кадастровый номер (обязательно)")
    title: str
    description: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    region_name: Optional[str] = None
    city_name: Optional[str] = None
    price: Optional[float] = None
    area: Optional[float] = None
    land_category: Optional[str] = None
    allowed_usage: Optional[str] = None
    deal_type: Optional[str] = None
    has_building: bool = False
    photos: List[str] = Field(default_factory=list)
    contact_phone: Optional[str] = None
    features: Optional[LandFeatureSchema] = None


class LandUpdate(BaseModel):
    """Land update schema"""

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    area: Optional[float] = None
    status: Optional[str] = None
    is_actual: Optional[bool] = None
    cadastral_number: Optional[str] = None
    photos: Optional[List[str]] = None
    has_building: Optional[bool] = None
    contact_phone: Optional[str] = None
    allowed_usage: Optional[str] = None


class LandListResponse(LandBase):
    """Land list response schema"""

    id: int
    status: str
    is_actual: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LandDetailResponse(LandBase):
    """Land detail response schema"""

    id: int
    external_id: Optional[str] = None
    source_id: Optional[int] = None
    region_id: int
    city_id: Optional[int] = None
    owner_user_id: Optional[int] = None
    status: str
    is_actual: bool
    published_at: Optional[datetime] = None
    features: Optional[LandFeatureSchema] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LandsFilterRequest(BaseModel):
    """Land filter request schema"""

    region_id: Optional[int] = None
    city_id: Optional[int] = None
    region_name: Optional[str] = None
    city_name: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    area_min: Optional[float] = None
    area_max: Optional[float] = None
    deal_type: Optional[str] = None
    listing_type: Optional[str] = None
    has_building: Optional[bool] = None
    land_category: Optional[str] = None
    search_query: Optional[str] = None
    cadastral_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bbox_radius_km: Optional[float] = Field(default=10, description="Radius in kilometers")
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
