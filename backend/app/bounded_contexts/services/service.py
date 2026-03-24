"""Services catalog service"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Category, Service
from app.schemas.service import (
    CategoryResponse,
    ServiceResponse,
    ServiceDetailResponse,
    ServiceCreate,
)


class ServicesService:
    """Service for managing service catalog"""

    @staticmethod
    def get_categories(db: Session) -> List[CategoryResponse]:
        """Get all service categories"""
        categories = (
            db.query(Category)
            .filter(Category.is_active == True)
            .order_by(Category.sort_order)
            .all()
        )
        return [CategoryResponse.from_orm(cat) for cat in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> CategoryResponse:
        """Get category by ID"""
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise NotFoundError("Category", category_id)

        return CategoryResponse.from_orm(category)

    @staticmethod
    def get_services(
        db: Session, category_id: Optional[int] = None
    ) -> List[ServiceResponse]:
        """Get all services, optionally filtered by category"""
        query = db.query(Service).filter(Service.is_active == True)

        if category_id:
            query = query.filter(Service.category_id == category_id)

        services = query.order_by(Service.priority.desc(), Service.name).all()
        return [ServiceResponse.from_orm(service) for service in services]

    @staticmethod
    def get_service_by_id(db: Session, service_id: int) -> ServiceDetailResponse:
        """Get service by ID with category information"""
        service = db.query(Service).filter(Service.id == service_id).first()

        if not service:
            raise NotFoundError("Service", service_id)

        # Load category
        category = (
            db.query(Category)
            .filter(Category.id == service.category_id)
            .first()
        )

        response = ServiceDetailResponse.from_orm(service)
        if category:
            response.category = CategoryResponse.from_orm(category)

        return response

    @staticmethod
    def get_services_by_ids(db: Session, service_ids: List[int]) -> List[Service]:
        """Get multiple services by IDs"""
        return db.query(Service).filter(Service.id.in_(service_ids)).all()

    @staticmethod
    def get_required_services(db: Session) -> List[ServiceResponse]:
        """Get services marked as required by default"""
        services = (
            db.query(Service)
            .filter(Service.is_active == True, Service.is_required_default == True)
            .order_by(Service.priority.desc())
            .all()
        )
        return [ServiceResponse.from_orm(service) for service in services]

    @staticmethod
    def create_service(db: Session, data: ServiceCreate) -> ServiceDetailResponse:
        """Create new service (admin only)"""
        # Verify category exists
        category = (
            db.query(Category)
            .filter(Category.id == data.category_id)
            .first()
        )
        if not category:
            raise NotFoundError("Category", data.category_id)

        service = Service(**data.dict())
        db.add(service)
        db.commit()
        db.refresh(service)

        return ServiceDetailResponse.from_orm(service)

    @staticmethod
    def search_services(db: Session, query: str) -> List[ServiceResponse]:
        """Full-text search in services"""
        search_pattern = f"%{query}%"
        services = (
            db.query(Service)
            .filter(
                Service.is_active == True,
                (Service.name.ilike(search_pattern) |
                 Service.short_description.ilike(search_pattern))
            )
            .order_by(Service.priority.desc())
            .all()
        )
        return [ServiceResponse.from_orm(service) for service in services]
