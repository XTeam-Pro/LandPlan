"""Company request/response schemas"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class CompanyBase(BaseModel):
    """Base company schema"""

    legal_name: str
    public_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Company creation schema"""

    pass


class CompanyUpdate(BaseModel):
    """Company update schema"""

    public_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = None


class CompanyServiceResponse(BaseModel):
    """Company service response"""

    id: int
    service_id: int
    service_name: str
    base_price_from: Optional[float] = None
    is_active: bool

    class Config:
        from_attributes = True


class CompanyListResponse(CompanyBase):
    """Company list response"""

    id: int
    rating: float
    reviews_count: int
    verification_status: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyDetailResponse(CompanyListResponse):
    """Company detail response"""

    services: Optional[List[CompanyServiceResponse]] = None
    region_ids: Optional[List[int]] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyFilterRequest(BaseModel):
    """Company filter request"""

    region_id: Optional[int] = None
    service_id: Optional[int] = None
    search_query: Optional[str] = None
    verification_status: Optional[str] = None
    sort_by: str = "rating"  # rating, name, created_at
    page: int = 1
    limit: int = 20
