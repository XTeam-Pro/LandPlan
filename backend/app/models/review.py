"""Review and rating models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class Review(Base):
    """User review of a company"""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    rating = Column(Float, default=0.0, nullable=False)  # 1-5 stars
    text = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, published, rejected
    is_verified_purchase = Column(String(50), default=False)  # Has user used this company
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    company = relationship("Company")

    def __repr__(self):
        return f"<Review {self.id} rating={self.rating}>"
