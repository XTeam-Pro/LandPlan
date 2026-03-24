"""Review schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreateSchema(BaseModel):
    """Create review request"""

    company_id: int
    rating: float = Field(ge=1.0, le=5.0, description="Rating from 1 to 5")
    text: Optional[str] = None


class ReviewUpdateSchema(BaseModel):
    """Update review request"""

    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    text: Optional[str] = None


class ReviewResponseSchema(BaseModel):
    """Review response"""

    id: int
    user_id: int
    company_id: int
    rating: float
    text: Optional[str] = None
    status: str
    is_verified_purchase: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewDetailSchema(ReviewResponseSchema):
    """Review with user/company info"""

    user_name: Optional[str] = None
    company_name: Optional[str] = None


class CompanyReviewsStatsSchema(BaseModel):
    """Statistics for company reviews"""

    company_id: int
    company_name: str
    average_rating: float
    total_reviews: int
    reviews_by_rating: dict  # {1: 5, 2: 3, 3: 10, 4: 25, 5: 50}
