"""Services catalog API routes"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.bounded_contexts.services.service import ServicesService
from app.db.session import get_db
from app.schemas.service import CategoryResponse, ServiceResponse, ServiceDetailResponse

router = APIRouter(prefix="/api/v1", tags=["Services & Categories"])


@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all categories",
    description="Get list of all service categories",
)
async def get_categories(db: Session = Depends(get_db)):
    """
    Get all service categories.

    Service categories organize services into logical groups:
    - Анализ воды (Water Analysis)
    - Геология (Geology)
    - Кадастр (Cadastre)
    - Юристы (Legal)
    - Строительство (Construction)
    - And 9 more...

    **Returns:**
    - List of all active categories
    - Sorted by priority
    """
    return ServicesService.get_categories(db)


@router.get(
    "/services",
    response_model=List[ServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get services",
    description="Get list of services with optional filtering",
)
async def get_services(
    category_id: int = Query(None, description="Filter by category ID"),
    search: str = Query(None, description="Full-text search query"),
    db: Session = Depends(get_db),
):
    """
    Get list of services.

    **Query Parameters:**
    - **category_id**: Filter services by category (optional)
    - **search**: Full-text search in service names and descriptions (optional)

    **Returns:**
    - List of services
    - Sorted by priority (required services first)
    """
    if search:
        return ServicesService.search_services(db, search)

    return ServicesService.get_services(db, category_id)


@router.get(
    "/services/{service_id}",
    response_model=ServiceDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service details",
    description="Get detailed information about a specific service",
)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a service.

    **Parameters:**
    - **service_id**: ID of the service

    **Returns:**
    - Service details including:
      - Name, description
      - Category information
      - Whether it's required by default
      - Priority level
    """
    return ServicesService.get_service_by_id(db, service_id)


@router.get(
    "/services/required",
    response_model=List[ServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get required services",
    description="Get services that are required by default",
)
async def get_required_services(db: Session = Depends(get_db)):
    """
    Get services marked as required by default.

    These are services that should typically be included in any land development plan.
    For example:
    - Cadastral survey (if boundaries not defined)
    - Legal support (if purchasing land)
    - Water analysis (if no water supply)

    **Returns:**
    - List of required services sorted by priority
    """
    return ServicesService.get_required_services(db)
