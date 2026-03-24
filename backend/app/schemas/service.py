"""Service request/response schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Base category schema"""

    name: str
    slug: str
    icon: Optional[str] = None
    sort_order: int = 0


class CategoryResponse(CategoryBase):
    """Category response schema"""

    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ServiceBase(BaseModel):
    """Base service schema"""

    name: str
    slug: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    is_required_default: bool = False
    priority: int = 0


class ServiceCreate(ServiceBase):
    """Service creation schema"""

    category_id: int


class ServiceResponse(ServiceBase):
    """Service response schema"""

    id: int
    category_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceDetailResponse(ServiceResponse):
    """Service detail response with category"""

    category: Optional[CategoryResponse] = None
