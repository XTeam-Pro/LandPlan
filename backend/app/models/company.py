"""Company models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Company(Base):
    """Company offering services"""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    legal_name = Column(String(255), nullable=False)
    public_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)

    # Rating and reviews
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)

    # Contact info
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)

    # Status
    verification_status = Column(String(50), default="pending")  # pending, verified, rejected, suspended
    is_active = Column(Boolean, default=True)

    # Admin-controlled display order (lower = shown first, for monetization)
    display_order = Column(Integer, default=1000, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    regions = relationship("CompanyRegion", back_populates="company", cascade="all, delete-orphan")
    services = relationship("CompanyService", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company {self.public_name}>"


class CompanyRegion(Base):
    """Company region presence"""

    __tablename__ = "company_regions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="regions")
    region = relationship("Region")

    def __repr__(self):
        return f"<CompanyRegion company_id={self.company_id}>"


class CompanyService(Base):
    """Company service offering"""

    __tablename__ = "company_services"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    base_price_from = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="services")
    service = relationship("Service")

    def __repr__(self):
        return f"<CompanyService company_id={self.company_id} service_id={self.service_id}>"
