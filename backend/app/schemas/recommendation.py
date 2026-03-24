"""Recommendation schemas"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ServiceRecommendationSchema(BaseModel):
    """Single service recommendation"""

    service_id: int
    service_slug: str
    service_name: str
    priority: str  # critical, recommended, optional
    reason: str
    step_order: int = 0

    class Config:
        from_attributes = True


class RecommendationsResponseSchema(BaseModel):
    """Full recommendations for a land"""

    land_id: int
    services: List[ServiceRecommendationSchema]
    summary: str
    total_critical: int
    total_recommended: int
    total_optional: int


class LandPlanStepSchema(BaseModel):
    """Single step in land plan"""

    id: int
    service_id: int
    service_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    order: int
    priority: int
    status: str  # pending, in_progress, completed, skipped
    selected_company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LandPlanCreateSchema(BaseModel):
    """Create land plan request"""

    land_id: int
    selected_service_ids: List[int]


class LandPlanUpdateSchema(BaseModel):
    """Update land plan request"""

    status: Optional[str] = None
    summary: Optional[str] = None


class LandPlanStepUpdateSchema(BaseModel):
    """Update land plan step"""

    status: Optional[str] = None
    selected_company_id: Optional[int] = None


class LandPlanDetailSchema(BaseModel):
    """Detailed land plan response"""

    id: int
    user_id: int
    land_id: int
    status: str
    summary: Optional[str] = None
    steps: List[LandPlanStepSchema]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LandPlanListSchema(BaseModel):
    """Land plan list response"""

    id: int
    land_id: int
    status: str
    summary: Optional[str] = None
    step_count: int
    completed_steps: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
