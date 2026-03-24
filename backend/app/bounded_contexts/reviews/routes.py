"""Reviews API routes"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.bounded_contexts.reviews.service import ReviewsService
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.review import (
    ReviewCreateSchema,
    ReviewUpdateSchema,
    ReviewResponseSchema,
    ReviewDetailSchema,
    CompanyReviewsStatsSchema,
)

router = APIRouter(prefix="/api/v1", tags=["Reviews"])


@router.post(
    "/companies/{company_id}/reviews",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create review",
    description="User creates review for a company",
)
async def create_review(
    company_id: int,
    review_data: ReviewCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new review for a company.

    **Parameters:**
    - **company_id**: ID of the company to review
    - **rating**: Rating from 1 to 5
    - **text**: Optional review text

    **Returns:**
    - Created review with status "pending" (needs moderation)

    **Restrictions:**
    - User can only review a company once
    - Review must be for a company the user has worked with or received services from
    """
    # Set company_id from URL path
    review_data.company_id = company_id
    return ReviewsService.create_review(db, current_user["user_id"], review_data)


@router.get(
    "/companies/{company_id}/reviews",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get company reviews",
    description="Get published reviews and statistics for a company",
)
async def get_company_reviews(
    company_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all published reviews for a company with statistics.

    **Parameters:**
    - **company_id**: ID of the company

    **Returns:**
    - List of published reviews with user information
    - Statistics: average rating, total count, breakdown by rating

    **Note:**
    - Only shows published reviews (approved by moderators)
    - Pending and rejected reviews are not shown
    """
    reviews, stats = ReviewsService.get_company_reviews(db, company_id)
    return {
        "reviews": reviews,
        "stats": stats,
    }


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update review",
    description="Update own review",
)
async def update_review(
    review_id: int,
    review_data: ReviewUpdateSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update own review.

    **Parameters:**
    - **review_id**: ID of the review to update
    - **rating**: New rating (optional)
    - **text**: New review text (optional)

    **Returns:**
    - Updated review with status reset to "pending"

    **Restrictions:**
    - User can only update their own reviews
    - Updated review goes back to pending status for re-moderation
    """
    return ReviewsService.update_review(db, review_id, current_user["user_id"], review_data)


@router.delete(
    "/reviews/{review_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete review",
    description="Delete own review",
)
async def delete_review(
    review_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete own review.

    **Parameters:**
    - **review_id**: ID of the review to delete

    **Returns:**
    - Confirmation message

    **Restrictions:**
    - User can only delete their own reviews
    """
    return ReviewsService.delete_review(db, review_id, current_user["user_id"])


@router.post(
    "/reviews/{review_id}/approve",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Approve review (admin/moderator)",
    description="Approve review for publishing",
)
async def approve_review(
    review_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve review for publishing (admin/moderator only).

    **Parameters:**
    - **review_id**: ID of the review to approve

    **Returns:**
    - Approved review with status "published"

    **Restrictions:**
    - Admin/moderator role required
    """
    # TODO: Add role check for admin/moderator
    return ReviewsService.approve_review(db, review_id)


@router.post(
    "/reviews/{review_id}/reject",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Reject review (admin/moderator)",
    description="Reject review from publishing",
)
async def reject_review(
    review_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reject review (admin/moderator only).

    **Parameters:**
    - **review_id**: ID of the review to reject

    **Returns:**
    - Rejected review with status "rejected"

    **Restrictions:**
    - Admin/moderator role required
    """
    # TODO: Add role check for admin/moderator
    return ReviewsService.reject_review(db, review_id)
