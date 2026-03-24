"""Recommendations and Land Plan service"""

from typing import List, Dict, Any
from dataclasses import asdict
from sqlalchemy.orm import Session
from datetime import datetime

from app.bounded_contexts.recommendations.engine import RecommendationEngine
from app.core.exceptions import NotFoundError, ValidationError
from app.models import (
    Land,
    LandFeature,
    LandPlan,
    LandPlanStep,
    Service,
    LandRecommendation,
)
from app.schemas.recommendation import (
    RecommendationsResponseSchema,
    LandPlanDetailSchema,
    LandPlanCreateSchema,
    LandPlanUpdateSchema,
    LandPlanStepUpdateSchema,
)


class RecommendationsService:
    """Service for recommendations and land planning"""

    @staticmethod
    def _serialize_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert engine result to JSON-serializable dict for caching."""
        return {
            'services': [
                {
                    'service_id': s.service_id,
                    'service_slug': s.service_slug,
                    'service_name': s.service_name,
                    'priority': s.priority.value if hasattr(s.priority, 'value') else s.priority,
                    'reason': s.reason,
                    'step_order': s.step_order,
                }
                for s in result['services']
            ],
            'summary': result['summary'],
            'total_critical': result['total_critical'],
            'total_recommended': result['total_recommended'],
            'total_optional': result['total_optional'],
        }

    @staticmethod
    def get_recommendations(
        db: Session, land_id: int
    ) -> RecommendationsResponseSchema:
        """
        Get recommendations for a land parcel.

        First checks cache, then computes if needed.
        """

        # Get land with features
        land = db.query(Land).filter(Land.id == land_id).first()
        if not land:
            raise NotFoundError("Land", land_id)

        features = db.query(LandFeature).filter(LandFeature.land_id == land_id).first()
        if not features:
            raise NotFoundError("Land features", land_id)

        # Try to get cached recommendations
        cached = (
            db.query(LandRecommendation)
            .filter(LandRecommendation.land_id == land_id)
            .first()
        )

        if cached and (cached.expires_at is None or cached.expires_at > datetime.utcnow()):
            # Return cached version
            return RecommendationsResponseSchema(
                land_id=land_id,
                **cached.recommendations
            )

        # Generate recommendations
        result = RecommendationEngine.get_recommendations(land, features)

        # Serialize for JSON storage and response
        serialized = RecommendationsService._serialize_result(result)

        # Cache the result
        recommendation = LandRecommendation(
            land_id=land_id,
            recommendations=serialized,
        )
        db.merge(recommendation)
        db.commit()

        return RecommendationsResponseSchema(
            land_id=land_id,
            **serialized
        )

    @staticmethod
    def create_land_plan(
        db: Session, user_id: int, data: LandPlanCreateSchema
    ) -> LandPlanDetailSchema:
        """Create a new land plan based on recommendations"""

        # Verify land exists
        land = db.query(Land).filter(Land.id == data.land_id).first()
        if not land:
            raise NotFoundError("Land", data.land_id)

        # Check if plan already exists for this land
        existing = (
            db.query(LandPlan)
            .filter(LandPlan.user_id == user_id, LandPlan.land_id == data.land_id)
            .first()
        )
        if existing:
            raise ValidationError("Plan for this land already exists")

        # Verify all services exist
        if not data.selected_service_ids:
            raise ValidationError("Must select at least one service")

        services = db.query(Service).filter(
            Service.id.in_(data.selected_service_ids)
        ).all()

        if len(services) != len(data.selected_service_ids):
            raise ValidationError("Some services not found")

        # Create plan
        plan = LandPlan(
            user_id=user_id,
            land_id=data.land_id,
            status="active",
            summary=f"Development plan for {land.title}",
        )
        db.add(plan)
        db.flush()  # Get plan.id

        # Create steps for each service
        for order, service in enumerate(services, 1):
            step = LandPlanStep(
                land_plan_id=plan.id,
                service_id=service.id,
                title=service.name,
                description=service.short_description,
                order=order,
                priority=order,
                status="pending",
            )
            db.add(step)

        db.commit()
        db.refresh(plan)

        # Load steps with service details
        steps = db.query(LandPlanStep).filter(
            LandPlanStep.land_plan_id == plan.id
        ).order_by(LandPlanStep.order).all()

        return LandPlanDetailSchema(
            id=plan.id,
            user_id=plan.user_id,
            land_id=plan.land_id,
            status=plan.status,
            summary=plan.summary,
            steps=[LandPlanDetailSchema.from_orm(step) for step in steps],
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )

    @staticmethod
    def get_land_plan(db: Session, plan_id: int) -> LandPlanDetailSchema:
        """Get land plan by ID"""
        plan = db.query(LandPlan).filter(LandPlan.id == plan_id).first()

        if not plan:
            raise NotFoundError("Land plan", plan_id)

        return LandPlanDetailSchema.from_orm(plan)

    @staticmethod
    def update_land_plan(
        db: Session, plan_id: int, data: LandPlanUpdateSchema
    ) -> LandPlanDetailSchema:
        """Update land plan metadata"""
        plan = db.query(LandPlan).filter(LandPlan.id == plan_id).first()

        if not plan:
            raise NotFoundError("Land plan", plan_id)

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)

        db.commit()
        db.refresh(plan)

        return LandPlanDetailSchema.from_orm(plan)

    @staticmethod
    def update_land_plan_step(
        db: Session, step_id: int, data: LandPlanStepUpdateSchema
    ):
        """Update land plan step (status, selected company)"""
        step = db.query(LandPlanStep).filter(LandPlanStep.id == step_id).first()

        if not step:
            raise NotFoundError("Land plan step", step_id)

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(step, field, value)

        db.commit()
        db.refresh(step)

        return step

    @staticmethod
    def get_user_land_plans(db: Session, user_id: int) -> List[LandPlanDetailSchema]:
        """Get all land plans for a user"""
        plans = (
            db.query(LandPlan)
            .filter(LandPlan.user_id == user_id)
            .order_by(LandPlan.updated_at.desc())
            .all()
        )

        return [LandPlanDetailSchema.from_orm(plan) for plan in plans]

    @staticmethod
    def complete_land_plan_step(
        db: Session, step_id: int
    ):
        """Mark land plan step as completed"""
        step = db.query(LandPlanStep).filter(LandPlanStep.id == step_id).first()

        if not step:
            raise NotFoundError("Land plan step", step_id)

        if step.status == "completed":
            raise ValidationError("Step already completed")

        step.status = "completed"
        db.commit()
        db.refresh(step)

        return step

    @staticmethod
    def recompute_recommendations(db: Session, land_id: int):
        """Recompute recommendations for a land (after features update)"""
        land = db.query(Land).filter(Land.id == land_id).first()
        if not land:
            raise NotFoundError("Land", land_id)

        features = db.query(LandFeature).filter(LandFeature.land_id == land_id).first()
        if not features:
            raise NotFoundError("Land features", land_id)

        # Generate fresh recommendations
        result = RecommendationEngine.get_recommendations(land, features)
        serialized = RecommendationsService._serialize_result(result)

        # Update cache
        recommendation = LandRecommendation(
            land_id=land_id,
            recommendations=serialized,
        )
        db.merge(recommendation)
        db.commit()

        return RecommendationsResponseSchema(
            land_id=land_id,
            **serialized
        )
