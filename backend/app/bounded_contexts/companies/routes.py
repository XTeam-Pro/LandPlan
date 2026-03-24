"""Companies API routes"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.bounded_contexts.companies.service import CompaniesService
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
    CompanyDetailResponse,
    CompanyServiceResponse,
    CompanyFilterRequest,
)

router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])


@router.get(
    "",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Search companies",
    description="Get list of companies with filtering",
)
async def list_companies(
    region_id: int = Query(None, description="Filter by region ID"),
    service_id: int = Query(None, description="Filter by service ID"),
    search_query: str = Query(None, description="Full-text search"),
    verification_status: str = Query(None, description="Filter by verification status"),
    sort_by: str = Query("rating", description="Sort by: rating, name, created_at"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search and filter companies.

    **Query Parameters:**
    - **region_id**: Filter companies operating in region
    - **service_id**: Filter companies offering service
    - **search_query**: Full-text search in name and description
    - **verification_status**: Filter by status (pending, verified, rejected)
    - **sort_by**: Sort by rating (default), name, or created_at
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)

    **Returns:**
    - List of companies matching filters
    - Total count and pagination info
    """

    filters = CompanyFilterRequest(
        region_id=region_id,
        service_id=service_id,
        search_query=search_query,
        verification_status=verification_status,
        sort_by=sort_by,
        page=page,
        limit=limit,
    )

    companies, total = CompaniesService.get_companies(db, filters)

    return {
        "items": companies,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get(
    "/{company_id}",
    response_model=CompanyDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get company details",
    description="Get detailed information about a company",
)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a company.

    **Parameters:**
    - **company_id**: ID of the company

    **Returns:**
    - Company details including:
      - Name, description, logo
      - Contact information
      - Rating and review count
      - List of services offered
      - Regions where company operates
      - Verification status
    """
    return CompaniesService.get_company_by_id(db, company_id)


@router.get(
    "/{company_id}/services",
    response_model=List[CompanyServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get company services",
    description="Get list of services offered by company",
)
async def get_company_services(company_id: int, db: Session = Depends(get_db)):
    """
    Get services offered by a company.

    **Parameters:**
    - **company_id**: ID of the company

    **Returns:**
    - List of services with pricing information
    """
    detail = CompaniesService.get_company_by_id(db, company_id)
    return detail.services or []


@router.get(
    "/by-service/{service_id}",
    response_model=List[CompanyDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get companies by service",
    description="Get verified companies offering a specific service",
)
async def get_companies_by_service(
    service_id: int,
    region_id: int = Query(None, description="Filter by region"),
    db: Session = Depends(get_db),
):
    """
    Get verified companies offering a specific service.

    This endpoint is useful for recommendations - after determining a land needs
    a service, you can call this to find available contractors.

    **Parameters:**
    - **service_id**: ID of the service
    - **region_id**: Optional - filter by region

    **Returns:**
    - List of verified companies offering this service
    - Sorted by rating (highest first)
    """
    return CompaniesService.get_companies_by_service(db, service_id, region_id)


@router.post(
    "",
    response_model=CompanyDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new company",
    description="Company self-registration (requires company role)",
)
async def register_company(
    company_data: CompanyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Register a new company.

    **Note:** User must have company role. After registration, company
    must be verified by admin before appearing in searches.

    **Parameters:**
    - **legal_name**: Legal company name
    - **public_name**: Public display name
    - **description**: Company description
    - **contact_email**: Contact email
    - **contact_phone**: Contact phone
    - Other optional fields

    **Returns:**
    - Created company with pending verification status
    """
    return CompaniesService.create_company(db, company_data, current_user["user_id"])


@router.patch(
    "/{company_id}",
    response_model=CompanyDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update company",
    description="Update company information (company owner only)",
)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update company information.

    **Parameters:**
    - **company_id**: ID of company to update
    - **company_data**: Fields to update (all optional)

    **Returns:**
    - Updated company information
    """
    return CompaniesService.update_company(db, company_id, company_data)


@router.post(
    "/{company_id}/services/{service_id}",
    response_model=CompanyServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add service to company",
    description="Company adds a service it offers",
)
async def add_service_to_company(
    company_id: int,
    service_id: int,
    base_price_from: float = Query(None, description="Base price for this service"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a service to company's offerings.

    **Parameters:**
    - **company_id**: ID of the company
    - **service_id**: ID of the service to add
    - **base_price_from**: Optional starting price

    **Returns:**
    - Service added to company profile
    """
    return CompaniesService.add_service(db, company_id, service_id, base_price_from)


@router.post(
    "/{company_id}/regions/{region_id}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add region to company",
    description="Company adds a region where it operates",
)
async def add_region_to_company(
    company_id: int,
    region_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a region where company operates.

    **Parameters:**
    - **company_id**: ID of the company
    - **region_id**: ID of the region

    **Returns:**
    - Region added to company profile
    """
    return CompaniesService.add_region(db, company_id, region_id)
