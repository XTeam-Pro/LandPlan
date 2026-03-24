"""Land and LandFeature models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.base import Base


class Land(Base):
    """Land parcel model"""

    __tablename__ = "lands"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Cadastral number — required for publication
    cadastral_number = Column(String(50), nullable=True, index=True)

    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=False)

    # Geographic data
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    geom = Column(Geometry("POINT"), nullable=True, index=True)

    # Photos
    photos = Column(JSON, default=list, nullable=False)  # list of photo URLs

    # Land characteristics
    price = Column(Float, nullable=True)
    area = Column(Float, nullable=True)  # in square meters
    land_category = Column(String(100), nullable=True)  # e.g., "agricultural", "residential"
    allowed_usage = Column(String(255), nullable=True)  # Вид разрешённого использования
    deal_type = Column(String(50), nullable=True)  # purchase, rent, lease, auction

    # Listing type: import, owner, agency
    listing_type = Column(String(50), default="import", nullable=False)

    # Building info
    has_building = Column(Boolean, default=False, nullable=False)

    # Contact info for owner listings
    contact_phone = Column(String(20), nullable=True)

    # Status
    status = Column(String(50), default="active")  # active, sold, removed, pending_moderation
    is_actual = Column(Boolean, default=True)

    # Timestamps
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    features = relationship(
        "LandFeature",
        back_populates="land",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Land {self.title}>"


class LandFeature(Base):
    """Land features/characteristics"""

    __tablename__ = "land_features"

    id = Column(Integer, primary_key=True, index=True)
    land_id = Column(Integer, ForeignKey("lands.id"), unique=True, nullable=False)

    # Utilities
    has_water = Column(Boolean, default=False)
    has_electricity = Column(Boolean, default=False)
    has_gas = Column(Boolean, default=False)
    has_roads = Column(Boolean, default=False)

    # Land preparation
    boundaries_defined = Column(Boolean, default=False)
    build_ready = Column(Boolean, default=False)

    # Additional notes
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    land = relationship("Land", back_populates="features")

    def __repr__(self):
        return f"<LandFeature land_id={self.land_id}>"
