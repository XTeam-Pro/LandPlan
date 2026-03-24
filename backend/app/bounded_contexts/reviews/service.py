"""Reviews service"""

from typing import List, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models import Review, Company, User
from app.schemas.review import (
    ReviewCreateSchema,
    ReviewUpdateSchema,
    ReviewResponseSchema,
    ReviewDetailSchema,
    CompanyReviewsStatsSchema,
)


class ReviewsService:
    """Service for managing company reviews"""

    @staticmethod
    def create_review(
        db: Session, user_id: int, data: ReviewCreateSchema
    ) -> ReviewResponseSchema:
        """Create a review for a company"""

        # Verify company exists
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise NotFoundError("Company", data.company_id)

        # Check if user already reviewed this company
        existing = (
            db.query(Review)
            .filter(Review.user_id == user_id, Review.company_id == data.company_id)
            .first()
        )
        if existing:
            raise ConflictError("You already reviewed this company")

        # Create review
        review = Review(
            user_id=user_id,
            company_id=data.company_id,
            rating=data.rating,
            text=data.text,
            status="pending",  # Needs moderation
        )
        db.add(review)
        db.flush()

        # Update company rating
        ReviewsService._update_company_rating(db, data.company_id)

        db.commit()
        db.refresh(review)

        return ReviewResponseSchema.from_orm(review)

    @staticmethod
    def get_company_reviews(
        db: Session, company_id: int
    ) -> Tuple[List[ReviewDetailSchema], CompanyReviewsStatsSchema]:
        """Get reviews for a company with statistics"""

        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFoundError("Company", company_id)

        # Get approved reviews
        reviews = (
            db.query(Review)
            .filter(
                Review.company_id == company_id,
                Review.status == "published",
            )
            .order_by(Review.created_at.desc())
            .all()
        )

        # Build detailed responses
        review_details = []
        for review in reviews:
            user = db.query(User).filter(User.id == review.user_id).first()
            detail = ReviewDetailSchema.from_orm(review)
            detail.user_name = user.full_name if user else "Anonymous"
            detail.company_name = company.public_name
            review_details.append(detail)

        # Calculate stats
        stats = ReviewsService._calculate_review_stats(db, company_id)

        return review_details, stats

    @staticmethod
    def update_review(
        db: Session, review_id: int, user_id: int, data: ReviewUpdateSchema
    ) -> ReviewResponseSchema:
        """Update user's own review"""

        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundError("Review", review_id)

        if review.user_id != user_id:
            raise ValidationError("Cannot update other user's review")

        if data.rating:
            review.rating = data.rating
        if data.text is not None:
            review.text = data.text

        # Reset to pending since content changed
        review.status = "pending"

        db.commit()
        db.refresh(review)

        # Update company rating
        ReviewsService._update_company_rating(db, review.company_id)

        return ReviewResponseSchema.from_orm(review)

    @staticmethod
    def delete_review(db: Session, review_id: int, user_id: int) -> dict:
        """Delete user's own review"""

        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundError("Review", review_id)

        if review.user_id != user_id:
            raise ValidationError("Cannot delete other user's review")

        company_id = review.company_id
        db.delete(review)
        db.commit()

        # Update company rating
        ReviewsService._update_company_rating(db, company_id)

        return {"message": "Review deleted"}

    @staticmethod
    def approve_review(db: Session, review_id: int) -> ReviewResponseSchema:
        """Approve review for publishing (admin/moderator)"""

        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundError("Review", review_id)

        review.status = "published"
        db.commit()
        db.refresh(review)

        return ReviewResponseSchema.from_orm(review)

    @staticmethod
    def reject_review(db: Session, review_id: int) -> ReviewResponseSchema:
        """Reject review (admin/moderator)"""

        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundError("Review", review_id)

        review.status = "rejected"
        db.commit()
        db.refresh(review)

        return ReviewResponseSchema.from_orm(review)

    @staticmethod
    def _update_company_rating(db: Session, company_id: int):
        """Recalculate and update company rating from reviews"""

        result = (
            db.query(func.avg(Review.rating))
            .filter(
                Review.company_id == company_id,
                Review.status == "published",
            )
            .first()
        )

        average_rating = float(result[0]) if result[0] else 0.0

        count = (
            db.query(func.count(Review.id))
            .filter(
                Review.company_id == company_id,
                Review.status == "published",
            )
            .first()
        )

        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            company.rating = average_rating
            company.reviews_count = count[0] if count else 0
            db.commit()

    @staticmethod
    def _calculate_review_stats(
        db: Session, company_id: int
    ) -> CompanyReviewsStatsSchema:
        """Calculate review statistics for company"""

        company = db.query(Company).filter(Company.id == company_id).first()

        # Count reviews by rating
        reviews_by_rating = {}
        for rating in [1, 2, 3, 4, 5]:
            count = (
                db.query(func.count(Review.id))
                .filter(
                    Review.company_id == company_id,
                    Review.status == "published",
                    Review.rating == rating,
                )
                .first()
            )
            reviews_by_rating[str(rating)] = count[0] if count else 0

        return CompanyReviewsStatsSchema(
            company_id=company_id,
            company_name=company.public_name if company else "Unknown",
            average_rating=company.rating if company else 0.0,
            total_reviews=company.reviews_count if company else 0,
            reviews_by_rating=reviews_by_rating,
        )
