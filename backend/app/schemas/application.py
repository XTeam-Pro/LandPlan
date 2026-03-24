"""Application (request to contractor) schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApplicationCreateSchema(BaseModel):
    """Create application request"""

    land_id: int
    service_id: int
    company_id: int
    land_plan_step_id: Optional[int] = None
    message: Optional[str] = None


class ApplicationUpdateStatusSchema(BaseModel):
    """Update application status"""

    status: str  # pending, accepted, in_progress, completed, rejected, cancelled


class ApplicationResponseSchema(BaseModel):
    """Application response"""

    id: int
    user_id: int
    land_id: int
    service_id: int
    company_id: int
    land_plan_step_id: Optional[int] = None
    status: str
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetailSchema(ApplicationResponseSchema):
    """Detailed application with land/service/company info"""

    land_title: Optional[str] = None
    service_name: Optional[str] = None
    company_name: Optional[str] = None
    company_phone: Optional[str] = None
    company_email: Optional[str] = None


class ApplicationListSchema(BaseModel):
    """Application list item"""

    id: int
    land_title: str
    service_name: str
    company_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationStatsSchema(BaseModel):
    """Application statistics"""

    total: int
    pending: int
    accepted: int
    in_progress: int
    completed: int
    rejected: int
    cancelled: int
