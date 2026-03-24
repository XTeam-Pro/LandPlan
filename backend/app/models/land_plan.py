"""Land Plan models - the development roadmap for a land parcel"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class LandPlan(Base):
    """Land development plan for a specific land parcel"""

    __tablename__ = "land_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    land_id = Column(Integer, ForeignKey("lands.id"), nullable=False, unique=True, index=True)
    status = Column(String(50), default="active")  # active, paused, completed
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    steps = relationship(
        "LandPlanStep",
        back_populates="land_plan",
        cascade="all, delete-orphan",
        order_by="LandPlanStep.order",
    )

    def __repr__(self):
        return f"<LandPlan {self.id} land_id={self.land_id}>"


class LandPlanStep(Base):
    """Individual step/stage in a land development plan"""

    __tablename__ = "land_plan_steps"

    id = Column(Integer, primary_key=True, index=True)
    land_plan_id = Column(Integer, ForeignKey("land_plans.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)  # Sequence order
    priority = Column(Integer, default=0)  # 1=critical, 2=recommended, 3=optional
    status = Column(String(50), default="pending")  # pending, in_progress, completed, skipped
    selected_company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    land_plan = relationship("LandPlan", back_populates="steps")
    service = relationship("Service")
    selected_company = relationship("Company")

    def __repr__(self):
        return f"<LandPlanStep {self.id} service_id={self.service_id}>"
