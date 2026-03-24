"""Lands service"""

from typing import List, Optional, Tuple
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.core.exceptions import NotFoundError
from app.models import Land, LandFeature, Region, City
from app.schemas.land import (
    LandCreate,
    LandUpdate,
    LandListResponse,
    LandDetailResponse,
    LandsFilterRequest,
)


class LandsService:
    """Service for managing land parcels"""

    @staticmethod
    def get_lands(
        db: Session, filters: LandsFilterRequest
    ) -> Tuple[List[LandListResponse], int]:
        """Get lands with filtering and pagination"""

        # Build base query
        query = db.query(Land)

        # Apply filters
        if filters.region_id:
            query = query.filter(Land.region_id == filters.region_id)

        if filters.city_id:
            query = query.filter(Land.city_id == filters.city_id)

        if filters.price_min is not None:
            query = query.filter(Land.price >= filters.price_min)

        if filters.price_max is not None:
            query = query.filter(Land.price <= filters.price_max)

        if filters.area_min is not None:
            query = query.filter(Land.area >= filters.area_min)

        if filters.area_max is not None:
            query = query.filter(Land.area <= filters.area_max)

        if filters.deal_type:
            query = query.filter(Land.deal_type == filters.deal_type)

        # Full-text search
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    Land.title.ilike(search),
                    Land.description.ilike(search),
                    Land.address.ilike(search),
                )
            )

        # Geo-filtering (bounding box or radius)
        if filters.latitude is not None and filters.longitude is not None:
            # Simple distance calculation (works without PostGIS)
            radius_degrees = filters.bbox_radius_km / 111.0  # Rough conversion

            query = query.filter(
                and_(
                    Land.latitude.between(
                        filters.latitude - radius_degrees,
                        filters.latitude + radius_degrees,
                    ),
                    Land.longitude.between(
                        filters.longitude - radius_degrees,
                        filters.longitude + radius_degrees,
                    ),
                )
            )

        # Filter active lands
        query = query.filter(Land.status == "active", Land.is_actual == True)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (filters.page - 1) * filters.limit
        lands = query.offset(offset).limit(filters.limit).all()

        return [LandListResponse.from_orm(land) for land in lands], total

    @staticmethod
    def get_land_by_id(db: Session, land_id: int) -> LandDetailResponse:
        """Get land by ID with full details"""
        land = db.query(Land).filter(Land.id == land_id).first()

        if not land:
            raise NotFoundError("Land", land_id)

        return LandDetailResponse.from_orm(land)

    @staticmethod
    def create_land(db: Session, data: LandCreate) -> LandDetailResponse:
        """Create new land parcel"""
        # Check if region exists
        region = db.query(Region).filter(Region.id == data.region_id).first()
        if not region:
            raise NotFoundError("Region", data.region_id)

        # Create land
        land = Land(**data.dict(exclude_unset=True))
        db.add(land)
        db.flush()  # Get land.id

        # Create land features
        features = LandFeature(land_id=land.id)
        db.add(features)
        db.commit()
        db.refresh(land)

        return LandDetailResponse.from_orm(land)

    @staticmethod
    def update_land(db: Session, land_id: int, data: LandUpdate) -> LandDetailResponse:
        """Update land parcel"""
        land = db.query(Land).filter(Land.id == land_id).first()

        if not land:
            raise NotFoundError("Land", land_id)

        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(land, field, value)

        db.commit()
        db.refresh(land)

        return LandDetailResponse.from_orm(land)

    @staticmethod
    def get_land_features(db: Session, land_id: int):
        """Get land features/characteristics"""
        features = db.query(LandFeature).filter(LandFeature.land_id == land_id).first()

        if not features:
            raise NotFoundError("Land features", land_id)

        return features

    @staticmethod
    def get_land_companies(db: Session, land_id: int) -> dict:
        """Get relevant companies for a land parcel based on recommendations."""
        from app.models import Company, CompanyService, CompanyRegion, LandFeature, Service
        from app.bounded_contexts.recommendations.engine import RecommendationEngine

        land = db.query(Land).filter(Land.id == land_id).first()
        if not land:
            raise NotFoundError("Land", land_id)

        features = db.query(LandFeature).filter(LandFeature.land_id == land_id).first()
        if not features:
            raise NotFoundError("Land features", land_id)

        # Get recommendations
        result = RecommendationEngine.get_recommendations(land, features)
        service_ids = [s.service_id for s in result['services']]

        # Find companies offering these services in this region
        companies_by_service = []
        for rec in result['services']:
            companies = (
                db.query(Company)
                .join(CompanyService, Company.id == CompanyService.company_id)
                .join(CompanyRegion, Company.id == CompanyRegion.company_id)
                .filter(
                    CompanyService.service_id == rec.service_id,
                    CompanyService.is_active == True,
                    CompanyRegion.region_id == land.region_id,
                    Company.is_active == True,
                )
                .order_by(Company.rating.desc())
                .all()
            )

            companies_by_service.append({
                "service_id": rec.service_id,
                "service_name": rec.service_name,
                "priority": rec.priority.value if hasattr(rec.priority, 'value') else rec.priority,
                "companies": [
                    {
                        "id": c.id,
                        "public_name": c.public_name,
                        "rating": c.rating,
                        "reviews_count": c.reviews_count,
                        "verification_status": c.verification_status,
                        "contact_phone": c.contact_phone,
                        "contact_email": c.contact_email,
                    }
                    for c in companies
                ]
            })

        return {
            "land_id": land_id,
            "region_id": land.region_id,
            "services_with_companies": companies_by_service,
        }

    @staticmethod
    def update_land_features(db: Session, land_id: int, features_data: dict):
        """Update land features"""
        features = db.query(LandFeature).filter(LandFeature.land_id == land_id).first()

        if not features:
            raise NotFoundError("Land features", land_id)

        for field, value in features_data.items():
            if hasattr(features, field):
                setattr(features, field, value)

        db.commit()
        db.refresh(features)

        return features
