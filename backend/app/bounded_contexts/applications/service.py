"""Applications service"""

from typing import List, Tuple
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models import Application, Land, Service, Company, User
from app.schemas.application import (
    ApplicationCreateSchema,
    ApplicationUpdateStatusSchema,
    ApplicationResponseSchema,
    ApplicationDetailSchema,
    ApplicationListSchema,
    ApplicationStatsSchema,
)


class ApplicationsService:
    """Service for managing applications/requests to contractors"""

    @staticmethod
    def create_application(
        db: Session, user_id: int, data: ApplicationCreateSchema
    ) -> ApplicationResponseSchema:
        """Create new application/request"""

        # Verify entities exist
        land = db.query(Land).filter(Land.id == data.land_id).first()
        if not land:
            raise NotFoundError("Land", data.land_id)

        service = db.query(Service).filter(Service.id == data.service_id).first()
        if not service:
            raise NotFoundError("Service", data.service_id)

        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise NotFoundError("Company", data.company_id)

        # Check for duplicate application (same user, land, service, company)
        existing = (
            db.query(Application)
            .filter(
                Application.user_id == user_id,
                Application.land_id == data.land_id,
                Application.service_id == data.service_id,
                Application.company_id == data.company_id,
                Application.status.in_(["pending", "accepted", "in_progress"]),
            )
            .first()
        )
        if existing:
            raise ConflictError("Заявка на эту услугу уже существует")

        # Create application
        application = Application(
            user_id=user_id,
            land_id=data.land_id,
            service_id=data.service_id,
            company_id=data.company_id,
            land_plan_step_id=data.land_plan_step_id,
            message=data.message,
            status="pending",
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        return ApplicationResponseSchema.from_orm(application)

    @staticmethod
    def get_application(db: Session, application_id: int) -> ApplicationDetailSchema:
        """Get application by ID with related info"""
        application = (
            db.query(Application).filter(Application.id == application_id).first()
        )

        if not application:
            raise NotFoundError("Application", application_id)

        # Get related entities
        land = db.query(Land).filter(Land.id == application.land_id).first()
        service = db.query(Service).filter(Service.id == application.service_id).first()
        company = db.query(Company).filter(Company.id == application.company_id).first()

        response = ApplicationDetailSchema.from_orm(application)
        response.land_title = land.title if land else None
        response.service_name = service.name if service else None
        response.company_name = company.public_name if company else None
        response.company_phone = company.contact_phone if company else None
        response.company_email = company.contact_email if company else None

        return response

    @staticmethod
    def get_user_applications(
        db: Session, user_id: int, status_filter: str = None
    ) -> Tuple[List[ApplicationDetailSchema], int]:
        """Get applications for a user"""
        query = db.query(Application).filter(Application.user_id == user_id)

        if status_filter:
            query = query.filter(Application.status == status_filter)

        total = query.count()
        applications = query.order_by(Application.created_at.desc()).all()

        results = []
        for app in applications:
            land = db.query(Land).filter(Land.id == app.land_id).first()
            service = db.query(Service).filter(Service.id == app.service_id).first()
            company = db.query(Company).filter(Company.id == app.company_id).first()

            detail = ApplicationDetailSchema.from_orm(app)
            detail.land_title = land.title if land else None
            detail.service_name = service.name if service else None
            detail.company_name = company.public_name if company else None
            detail.company_phone = company.contact_phone if company else None
            detail.company_email = company.contact_email if company else None
            results.append(detail)

        return results, total

    @staticmethod
    def get_company_applications(
        db: Session, company_id: int, status_filter: str = None
    ) -> Tuple[List[ApplicationDetailSchema], int]:
        """Get applications for a company"""
        query = db.query(Application).filter(Application.company_id == company_id)

        if status_filter:
            query = query.filter(Application.status == status_filter)

        total = query.count()
        applications = query.order_by(Application.created_at.desc()).all()

        results = []
        for app in applications:
            land = db.query(Land).filter(Land.id == app.land_id).first()
            service = db.query(Service).filter(Service.id == app.service_id).first()
            user = db.query(User).filter(User.id == app.user_id).first()

            detail = ApplicationDetailSchema.from_orm(app)
            detail.land_title = land.title if land else None
            detail.service_name = service.name if service else None
            if user:
                detail.company_name = user.full_name  # Reuse field for user name
            results.append(detail)

        return results, total

    @staticmethod
    def update_application_status(
        db: Session, application_id: int, data: ApplicationUpdateStatusSchema
    ) -> ApplicationResponseSchema:
        """Update application status"""
        application = (
            db.query(Application).filter(Application.id == application_id).first()
        )

        if not application:
            raise NotFoundError("Application", application_id)

        # Validate status transitions
        valid_statuses = [
            "pending",
            "accepted",
            "rejected",
            "in_progress",
            "completed",
            "cancelled",
        ]
        if data.status not in valid_statuses:
            raise ValidationError(f"Недопустимый статус: {data.status}")

        # Some transitions are not allowed
        if application.status == "completed":
            raise ValidationError("Невозможно изменить статус завершённой заявки")

        application.status = data.status
        db.commit()
        db.refresh(application)

        return ApplicationResponseSchema.from_orm(application)

    @staticmethod
    def get_application_stats(
        db: Session, entity_type: str, entity_id: int
    ) -> ApplicationStatsSchema:
        """Get application statistics for user or company"""
        if entity_type == "user":
            query = db.query(Application).filter(Application.user_id == entity_id)
        elif entity_type == "company":
            query = db.query(Application).filter(Application.company_id == entity_id)
        else:
            raise ValidationError("Недопустимый тип сущности")

        total = query.count()
        pending = query.filter(Application.status == "pending").count()
        accepted = query.filter(Application.status == "accepted").count()
        in_progress = query.filter(Application.status == "in_progress").count()
        completed = query.filter(Application.status == "completed").count()
        rejected = query.filter(Application.status == "rejected").count()
        cancelled = query.filter(Application.status == "cancelled").count()

        return ApplicationStatsSchema(
            total=total,
            pending=pending,
            accepted=accepted,
            in_progress=in_progress,
            completed=completed,
            rejected=rejected,
            cancelled=cancelled,
        )

    @staticmethod
    def get_applications_by_land_plan_step(
        db: Session, land_plan_step_id: int
    ) -> List[ApplicationResponseSchema]:
        """Get all applications for a land plan step"""
        applications = (
            db.query(Application)
            .filter(Application.land_plan_step_id == land_plan_step_id)
            .all()
        )
        return [ApplicationResponseSchema.from_orm(app) for app in applications]
