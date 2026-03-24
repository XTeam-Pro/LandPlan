"""Admin API routes — user management, company verification, display order"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.core.security import get_current_admin, get_current_superadmin
from app.models.user import User
from app.models.company import Company

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# --- Schemas ---

class SetUserRoleRequest(BaseModel):
    role: str  # user, company, admin, moderator


class VerifyCompanyRequest(BaseModel):
    verification_status: str  # verified, rejected, suspended


class SetCompanyOrderRequest(BaseModel):
    display_order: int


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    status: str

    class Config:
        from_attributes = True


class CompanyAdminResponse(BaseModel):
    id: int
    legal_name: str
    public_name: str
    verification_status: str
    is_active: bool
    display_order: int

    class Config:
        from_attributes = True


# --- User management (superadmin only) ---

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_superadmin),
):
    """List all users (superadmin only)"""
    result = await db.execute(select(User).order_by(User.id))
    return result.scalars().all()


@router.patch("/users/{user_id}/role")
async def set_user_role(
    user_id: int,
    body: SetUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_superadmin),
):
    """Set user role — only superadmin can grant admin rights"""
    if body.role not in ("user", "company", "admin", "moderator"):
        raise HTTPException(status_code=400, detail="Invalid role")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent changing superadmin role
    if user.role == "superadmin":
        raise HTTPException(status_code=403, detail="Cannot change superadmin role")

    user.role = body.role
    await db.commit()
    return {"message": f"User {user_id} role set to {body.role}"}


# --- Company verification (admin) ---

@router.get("/companies/pending", response_model=list[CompanyAdminResponse])
async def list_pending_companies(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """List companies pending verification"""
    result = await db.execute(
        select(Company)
        .where(Company.verification_status == "pending")
        .order_by(Company.created_at)
    )
    return result.scalars().all()


@router.patch("/companies/{company_id}/verify")
async def verify_company(
    company_id: int,
    body: VerifyCompanyRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """Verify or reject a company (admin)"""
    if body.verification_status not in ("verified", "rejected", "suspended"):
        raise HTTPException(status_code=400, detail="Invalid verification status")

    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.verification_status = body.verification_status
    await db.commit()
    return {
        "message": f"Company {company_id} verification set to {body.verification_status}"
    }


# --- Company display order (admin, for monetization) ---

@router.patch("/companies/{company_id}/display-order")
async def set_company_display_order(
    company_id: int,
    body: SetCompanyOrderRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """Set company display order — lower number = shown first"""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.display_order = body.display_order
    await db.commit()
    return {
        "message": f"Company {company_id} display_order set to {body.display_order}"
    }


@router.get("/companies", response_model=list[CompanyAdminResponse])
async def list_all_companies_admin(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """List all companies with admin details"""
    result = await db.execute(
        select(Company).order_by(Company.display_order, Company.id)
    )
    return result.scalars().all()
