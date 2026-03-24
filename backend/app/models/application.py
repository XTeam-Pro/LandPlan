"""Application (Request to contractor) models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Application(Base):
    """User application/request to a contractor"""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    land_id = Column(Integer, ForeignKey("lands.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    land_plan_id = Column(Integer, ForeignKey("land_plans.id"), nullable=True)
    land_plan_step_id = Column(Integer, ForeignKey("land_plan_steps.id"), nullable=True)

    # Status
    status = Column(String(50), default="pending", index=True)  # pending, accepted, in_progress, completed, rejected, cancelled

    # Message from user
    message = Column(Text, nullable=True)

    # Snapshot of user contact info at time of application
    contact_snapshot = Column(Text, nullable=True)  # JSON snapshot

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Application {self.id} status={self.status}>"
