"""Recommendations and Land Plan API routes"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.bounded_contexts.recommendations.service import RecommendationsService
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.recommendation import (
    RecommendationsResponseSchema,
    LandPlanDetailSchema,
    LandPlanCreateSchema,
    LandPlanUpdateSchema,
    LandPlanStepUpdateSchema,
    LandPlanListSchema,
)

router = APIRouter(prefix="/api/v1", tags=["Recommendations & Land Plans"])


@router.get(
    "/lands/{land_id}/recommendations",
    response_model=RecommendationsResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get land recommendations",
    description="Get development recommendations for a land parcel",
)
async def get_recommendations(land_id: int, db: Session = Depends(get_db)):
    """
    Get development recommendations for a land parcel.

    This is the CORE of the system - it analyzes land characteristics and recommends
    the sequence of services needed for successful development.

    **Analysis includes:**
    - Water availability → water analysis, drilling, supply services
    - Boundary status → cadastral survey, boundary determination
    - Deal type → legal services, appraisal
    - Soil preparation → geological survey, engineering
    - Utilities → drainage, electricity connections

    **Returns:**
    - List of recommended services with priority levels (CRITICAL/RECOMMENDED/OPTIONAL)
    - Suggested execution sequence
    - Human-readable summary

    **Example response:**
    ```json
    {
      "land_id": 123,
      "services": [
        {
          "service_id": 1,
          "service_name": "Анализ воды",
          "priority": "critical",
          "reason": "Вода отсутствует - необходим анализ скважины",
          "step_order": 1
        },
        ...
      ],
      "total_critical": 3,
      "total_recommended": 5
    }
    ```
    """
    return RecommendationsService.get_recommendations(db, land_id)


@router.post(
    "/land-plans",
    response_model=LandPlanDetailSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create land plan",
    description="Create a development plan for a land parcel",
)
async def create_land_plan(
    plan_data: LandPlanCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a land development plan.

    After user sees recommendations for a land, they select which services to include
    in their plan. This creates a sequential roadmap with stages.

    **Parameters:**
    - **land_id**: ID of the land parcel
    - **selected_service_ids**: List of service IDs to include

    **Returns:**
    - Land plan with ordered steps
    - Each step has status (pending/in_progress/completed)
    - User can track progress and assign contractors

    **Flow:**
    1. User selects land → gets recommendations
    2. User clicks "Create Plan" → selects services
    3. System creates sequential plan with stages
    4. User can then:
       - Assign contractors to steps
       - Send applications
       - Track progress
    """
    return RecommendationsService.create_land_plan(
        db, current_user["user_id"], plan_data
    )


@router.get(
    "/land-plans/{plan_id}",
    response_model=LandPlanDetailSchema,
    status_code=status.HTTP_200_OK,
    summary="Get land plan details",
    description="Get detailed information about a land development plan",
)
async def get_land_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a land plan.

    **Returns:**
    - All plan steps in order
    - Current status of each step
    - Assigned contractor (if any)
    - Timeline and progress
    """
    return RecommendationsService.get_land_plan(db, plan_id)


@router.get(
    "/my-land-plans",
    response_model=List[LandPlanDetailSchema],
    status_code=status.HTTP_200_OK,
    summary="Get my land plans",
    description="Get all land plans for current user",
)
async def get_my_land_plans(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all land development plans for current user.

    **Returns:**
    - List of user's plans
    - Each with status and progress information
    """
    return RecommendationsService.get_user_land_plans(db, current_user["user_id"])


@router.patch(
    "/land-plans/{plan_id}",
    response_model=LandPlanDetailSchema,
    status_code=status.HTTP_200_OK,
    summary="Update land plan",
    description="Update land plan metadata",
)
async def update_land_plan(
    plan_id: int,
    plan_data: LandPlanUpdateSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update land plan (status, summary, etc).

    **Parameters:**
    - **status**: Plan status (active, paused, completed)
    - **summary**: Plan notes/summary

    **Returns:**
    - Updated land plan
    """
    return RecommendationsService.update_land_plan(db, plan_id, plan_data)


@router.patch(
    "/land-plan-steps/{step_id}",
    status_code=status.HTTP_200_OK,
    summary="Update land plan step",
    description="Update a specific step in a land plan",
)
async def update_land_plan_step(
    step_id: int,
    step_data: LandPlanStepUpdateSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a specific step in a land plan.

    **Parameters:**
    - **status**: Step status (pending, in_progress, completed, skipped)
    - **selected_company_id**: Assign contractor to this step

    **Use cases:**
    - User selects a contractor for a service → set selected_company_id
    - Contractor completes work → change status to "completed"
    - User decides not to do a service → set status to "skipped"

    **Returns:**
    - Updated step
    """
    return RecommendationsService.update_land_plan_step(db, step_id, step_data)


@router.post(
    "/land-plan-steps/{step_id}/complete",
    status_code=status.HTTP_200_OK,
    summary="Mark step as completed",
    description="Mark a land plan step as completed",
)
async def complete_step(
    step_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a land plan step as completed.

    **Returns:**
    - Updated step with status=completed
    """
    return RecommendationsService.complete_land_plan_step(db, step_id)
