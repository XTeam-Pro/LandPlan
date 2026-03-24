"""Applications API routes"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.bounded_contexts.applications.service import ApplicationsService
from app.core.security import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import Company, User
from app.schemas.application import (
    ApplicationCreateSchema,
    ApplicationUpdateStatusSchema,
    ApplicationResponseSchema,
    ApplicationDetailSchema,
    ApplicationStatsSchema,
)

router = APIRouter(prefix="/api/v1/applications", tags=["Applications"])


@router.post(
    "",
    response_model=ApplicationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create application",
    description="User sends request to contractor",
)
async def create_application(
    app_data: ApplicationCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new application/request to a contractor.

    This is how users submit requests to contractors for specific services on their land.

    **Parameters:**
    - **land_id**: ID of the land parcel
    - **service_id**: ID of the service needed
    - **company_id**: ID of the contractor
    - **land_plan_step_id**: Optional - which step in the plan
    - **message**: Optional - additional message to contractor

    **Returns:**
    - Created application with status "pending"

    **Workflow:**
    1. User sees recommendations for land
    2. User creates development plan
    3. User selects contractor for a step
    4. User sends application via this endpoint
    5. Contractor receives and processes the request
    """
    return ApplicationsService.create_application(db, current_user["user_id"], app_data)


@router.get(
    "",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get my applications",
    description="Get applications sent by current user or received by company",
)
async def get_my_applications(
    status_filter: str = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get applications for current user/company.

    For regular users: returns applications they sent.
    For companies: returns applications received.

    **Query Parameters:**
    - **status_filter**: Optional - filter by status
      (pending, accepted, in_progress, completed, rejected, cancelled)

    **Returns:**
    - List of applications
    - Total count
    """
    role = current_user.get("payload", {}).get("role", "user")

    if role == "company":
        # Find company owned by this user (by matching email)
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        company = None
        if user:
            company = db.query(Company).filter(Company.contact_email == user.email).first()
        if company:
            applications, total = ApplicationsService.get_company_applications(
                db, company.id, status_filter
            )
        else:
            applications, total = [], 0
    else:
        applications, total = ApplicationsService.get_user_applications(
            db, current_user["user_id"], status_filter
        )

    return {
        "items": applications,
        "total": total,
    }


@router.get(
    "/company-info",
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о компании текущего пользователя",
)
async def get_my_company_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise NotFoundError("User", current_user["user_id"])
    company = db.query(Company).filter(Company.contact_email == user.email).first()
    if not company:
        return {"company_id": None}
    return {"company_id": company.id, "company_name": company.public_name}


@router.get(
    "/stats",
    response_model=ApplicationStatsSchema,
    status_code=status.HTTP_200_OK,
    summary="Get application statistics",
    description="Get stats for current user/company applications",
)
async def get_application_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get statistics about applications.

    For users: stats on applications they sent.
    For companies: stats on applications received.

    **Returns:**
    - Total applications count
    - Count by status (pending, accepted, in_progress, completed, rejected, cancelled)
    """
    role = current_user.get("payload", {}).get("role", "user")

    if role == "company":
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        company = None
        if user:
            company = db.query(Company).filter(Company.contact_email == user.email).first()
        if company:
            return ApplicationsService.get_application_stats(db, "company", company.id)
        return ApplicationStatsSchema(total=0, pending=0, accepted=0, in_progress=0, completed=0, rejected=0, cancelled=0)

    return ApplicationsService.get_application_stats(db, "user", current_user["user_id"])


@router.get(
    "/{application_id}",
    response_model=ApplicationDetailSchema,
    status_code=status.HTTP_200_OK,
    summary="Get application details",
)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about an application.

    **Parameters:**
    - **application_id**: ID of the application

    **Returns:**
    - Application with full context:
      - Land details
      - Service details
      - Contractor contact info
      - Current status
    """
    return ApplicationsService.get_application(db, application_id)


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update application status",
    description="Update status of an application",
)
async def update_application_status(
    application_id: int,
    status_data: ApplicationUpdateStatusSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update application status.

    **Contractor workflow:**
    1. Application created with status "pending"
    2. Contractor views it
    3. Contractor accepts → status = "accepted"
    4. Contractor starts work → status = "in_progress"
    5. Contractor finishes → status = "completed"

    **Alternative:**
    - Contractor rejects → status = "rejected"
    - User cancels → status = "cancelled"

    **Parameters:**
    - **application_id**: ID of application to update
    - **status**: New status

    **Valid statuses:**
    - pending (initial)
    - accepted (contractor accepts)
    - in_progress (work started)
    - completed (work done)
    - rejected (contractor rejects)
    - cancelled (user cancels)

    **Returns:**
    - Updated application
    """
    return ApplicationsService.update_application_status(db, application_id, status_data)
