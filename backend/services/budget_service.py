"""
Budget service: setting per-category monthly limits and calculating
how much of each has been used.

The utilization MATH (_compute_utilization_rows) is kept separate from
the database query (get_budget_utilization) so it can be unit-tested
with plain dicts, independent of MySQL - same pattern as
analysis_service.py.
"""

from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.budget import Budget
from backend.models.expense import Expense

STATUS_OVER = "over_budget"
STATUS_NEAR = "near_limit"
STATUS_OK = "on_track"

NEAR_LIMIT_THRESHOLD_PERCENT = 80


def _status_for(percent_used: float) -> str:
    if percent_used >= 100:
        return STATUS_OVER
    if percent_used >= NEAR_LIMIT_THRESHOLD_PERCENT:
        return STATUS_NEAR
    return STATUS_OK


def _compute_utilization_rows(budgets: list[dict], spent_by_category: dict) -> list[dict]:
    """
    Pure function: given budget limits and actual spending per category,
    compute remaining amount, percent used, and status for each budget.
    No database access here - this is what gets unit-tested.
    """
    results = []
    for b in budgets:
        spent = spent_by_category.get(b["category"], 0.0)
        limit = b["monthly_limit"]
        percent_used = round((spent / limit) * 100, 1) if limit else 0.0
        results.append({
            "id": b["id"],
            "category": b["category"],
            "monthly_limit": round(limit, 2),
            "spent": round(spent, 2),
            "remaining": round(limit - spent, 2),
            "percent_used": percent_used,
            "status": _status_for(percent_used),
        })

    results.sort(key=lambda r: r["percent_used"], reverse=True)
    return results


def upsert_budget(
    db: Session, user_id: int, category: str, monthly_limit: Decimal, month_year: str
) -> Budget:
    """Create a budget, or update the limit if one already exists for
    this user/category/month (so setting a budget twice just updates it)."""
    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.category == category,
            Budget.month_year == month_year,
        )
        .first()
    )
    if existing:
        existing.monthly_limit = monthly_limit
        db.commit()
        db.refresh(existing)
        return existing

    budget = Budget(
        user_id=user_id, category=category, monthly_limit=monthly_limit, month_year=month_year
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget_id: int, user_id: int) -> bool:
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()
    if budget is None:
        return False
    db.delete(budget)
    db.commit()
    return True


def get_budget_utilization(db: Session, user_id: int, year: int, month: int) -> list[dict]:
    month_year = f"{year:04d}-{month:02d}"

    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.month_year == month_year)
        .all()
    )
    if not budgets:
        return []

    budget_dicts = [
        {"id": b.id, "category": b.category, "monthly_limit": float(b.monthly_limit)}
        for b in budgets
    ]

    spent_rows = (
        db.query(Expense.category, func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            func.year(Expense.expense_date) == year,
            func.month(Expense.expense_date) == month,
        )
        .group_by(Expense.category)
        .all()
    )
    spent_by_category = {category: float(total) for category, total in spent_rows}

    return _compute_utilization_rows(budget_dicts, spent_by_category)
