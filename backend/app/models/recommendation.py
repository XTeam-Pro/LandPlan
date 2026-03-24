"""Recommendation and import job models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class LandRecommendation(Base):
    """Cached recommendations for a land parcel"""

    __tablename__ = "land_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    land_id = Column(Integer, ForeignKey("lands.id"), unique=True, nullable=False, index=True)

    # JSON storage of recommendations
    recommendations = Column(JSON, default={}, nullable=False)  # { services: [...], steps: [...] }

    # Metadata
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # When this cache expires
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    land = relationship("Land")

    def __repr__(self):
        return f"<LandRecommendation {self.id} land_id={self.land_id}>"


class ImportJob(Base):
    """Record of a data import job"""

    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed

    # Statistics
    total_items = Column(Integer, default=0)
    imported_items = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    errors = Column(Integer, default=0)

    # Details
    error_log = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source = relationship("Source")

    def __repr__(self):
        return f"<ImportJob {self.id} source_id={self.source_id}>"
