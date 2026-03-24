"""Companies service"""

from typing import List, Optional, Tuple
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.models import Company, CompanyRegion, CompanyService, Service, User
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
    CompanyDetailResponse,
    CompanyServiceResponse,
    CompanyFilterRequest,
)


class CompaniesService:
    """Service for managing companies"""

    @staticmethod
    def get_companies(
        db: Session, filters: CompanyFilterRequest
    ) -> Tuple[List[CompanyListResponse], int]:
        """Get companies with filtering and pagination"""

        query = db.query(Company).filter(Company.is_active == True)

        # Filter by region
        if filters.region_id:
            query = query.join(CompanyRegion).filter(
                CompanyRegion.region_id == filters.region_id
            )

        # Filter by service
        if filters.service_id:
            query = query.join(CompanyService).filter(
                CompanyService.service_id == filters.service_id
            )

        # Filter by verification status
        if filters.verification_status:
            query = query.filter(
                Company.verification_status == filters.verification_status
            )

        # Full-text search
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    Company.public_name.ilike(search),
                    Company.legal_name.ilike(search),
                    Company.description.ilike(search),
                )
            )

        # Get total count
        total = query.count()

        # Sort
        if filters.sort_by == "rating":
            query = query.order_by(Company.rating.desc())
        elif filters.sort_by == "name":
            query = query.order_by(Company.public_name)
        else:  # created_at
            query = query.order_by(Company.created_at.desc())

        # Pagination
        offset = (filters.page - 1) * filters.limit
        companies = query.distinct().offset(offset).limit(filters.limit).all()

        return [CompanyListResponse.from_orm(co) for co in companies], total

    @staticmethod
    def get_company_by_id(db: Session, company_id: int) -> CompanyDetailResponse:
        """Get company by ID with services and regions"""
        company = db.query(Company).filter(Company.id == company_id).first()

        if not company:
            raise NotFoundError("Company", company_id)

        # Get services
        company_services = (
            db.query(CompanyService, Service)
            .join(Service)
            .filter(CompanyService.company_id == company_id)
            .all()
        )

        services = []
        for cs, service in company_services:
            services.append(
                CompanyServiceResponse(
                    id=cs.id,
                    service_id=service.id,
                    service_name=service.name,
                    base_price_from=cs.base_price_from,
                    is_active=cs.is_active,
                )
            )

        # Get regions
        company_regions = (
            db.query(CompanyRegion)
            .filter(CompanyRegion.company_id == company_id)
            .all()
        )
        region_ids = [cr.region_id for cr in company_regions]

        response = CompanyDetailResponse.from_orm(company)
        response.services = services
        response.region_ids = region_ids

        return response

    @staticmethod
    def create_company(
        db: Session, data: CompanyCreate, user_id: int
    ) -> CompanyDetailResponse:
        """Create new company (company self-registration)"""
        # Check if company with this email already exists
        existing = (
            db.query(Company)
            .filter(Company.contact_email == data.contact_email)
            .first()
        )
        if existing:
            raise ConflictError("Компания с таким email уже существует")

        company = Company(**data.dict())
        company.verification_status = "pending"
        db.add(company)
        db.flush()

        # Update user role to company
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = "company"

        db.commit()
        db.refresh(company)

        return CompanyDetailResponse.from_orm(company)

    @staticmethod
    def update_company(
        db: Session, company_id: int, data: CompanyUpdate
    ) -> CompanyDetailResponse:
        """Update company information"""
        company = db.query(Company).filter(Company.id == company_id).first()

        if not company:
            raise NotFoundError("Company", company_id)

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)

        return CompanyDetailResponse.from_orm(company)

    @staticmethod
    def add_service(
        db: Session, company_id: int, service_id: int, base_price_from: Optional[float] = None
    ) -> CompanyServiceResponse:
        """Add service to company"""
        # Check company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFoundError("Company", company_id)

        # Check service exists
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise NotFoundError("Service", service_id)

        # Check not duplicate
        existing = (
            db.query(CompanyService)
            .filter(
                CompanyService.company_id == company_id,
                CompanyService.service_id == service_id,
            )
            .first()
        )
        if existing:
            raise ConflictError("Компания уже предоставляет эту услугу")

        company_service = CompanyService(
            company_id=company_id,
            service_id=service_id,
            base_price_from=base_price_from,
        )
        db.add(company_service)
        db.commit()
        db.refresh(company_service)

        return CompanyServiceResponse(
            id=company_service.id,
            service_id=service.id,
            service_name=service.name,
            base_price_from=base_price_from,
            is_active=company_service.is_active,
        )

    @staticmethod
    def add_region(db: Session, company_id: int, region_id: int) -> dict:
        """Add region where company operates"""
        # Check company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFoundError("Company", company_id)

        # Check not duplicate
        existing = (
            db.query(CompanyRegion)
            .filter(
                CompanyRegion.company_id == company_id,
                CompanyRegion.region_id == region_id,
            )
            .first()
        )
        if existing:
            raise ConflictError("Компания уже работает в этом регионе")

        company_region = CompanyRegion(company_id=company_id, region_id=region_id)
        db.add(company_region)
        db.commit()
        db.refresh(company_region)

        return {"id": company_region.id, "company_id": company_id, "region_id": region_id}

    @staticmethod
    def get_companies_by_service(
        db: Session, service_id: int, region_id: Optional[int] = None
    ) -> List[CompanyDetailResponse]:
        """Get companies offering a specific service in a region"""
        query = (
            db.query(Company)
            .join(CompanyService)
            .filter(
                CompanyService.service_id == service_id,
                Company.is_active == True,
                Company.verification_status == "verified",
            )
        )

        if region_id:
            query = query.join(CompanyRegion).filter(
                CompanyRegion.region_id == region_id
            )

        query = query.order_by(Company.rating.desc())

        companies = query.distinct().all()
        return [CompanyDetailResponse.from_orm(co) for co in companies]
