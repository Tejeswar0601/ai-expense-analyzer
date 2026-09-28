"""
API routes for budgets.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.api.deps import get_current_user
from backend.schemas.budget_schema import BudgetSet, BudgetUtilizationOut
from backend.services import budget_service

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


@router.post("", status_code=status.HTTP_201_CREATED)
def set_budget(
    payload: BudgetSet,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a budget, or updates the limit if one already exists
    for this category/month (so setting it twice just updates it)."""
    budget = budget_service.upsert_budget(
        db, current_user.id, payload.category, payload.monthly_limit, payload.month_year
    )
    return {
        "id": budget.id,
        "category": budget.category,
        "monthly_limit": float(budget.monthly_limit),
        "month_year": budget.month_year,
    }


@router.get("/{year}/{month}", response_model=list[BudgetUtilizationOut])
def get_utilization(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    return budget_service.get_budget_utilization(db, current_user.id, year, month)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = budget_service.delete_budget(db, budget_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget not found")
    return None
