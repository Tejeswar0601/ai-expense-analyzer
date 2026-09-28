"""
Service layer for expenses.

This is where the actual business logic lives - talking to the database,
applying rules, etc. Keeping this separate from api/expenses.py means
the routes stay thin and the logic is reusable/testable.

Every function here takes a user_id and filters/sets it, so one
user's data is never visible to or editable by another user.
"""

from sqlalchemy.orm import Session
from backend.models.expense import Expense
from backend.schemas.expense_schema import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, expense_data: ExpenseCreate, user_id: int) -> Expense:
    new_expense = Expense(**expense_data.model_dump(), user_id=user_id)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)  # reload it so we get the generated id/created_at
    return new_expense


def get_expense(db: Session, expense_id: int, user_id: int) -> Expense | None:
    return (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == user_id)
        .first()
    )


def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Expense]:
    return (
        db.query(Expense)
        .filter(Expense.user_id == user_id)
        .order_by(Expense.expense_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_expense(
    db: Session, expense_id: int, expense_data: ExpenseUpdate, user_id: int
) -> Expense | None:
    expense = get_expense(db, expense_id, user_id)
    if expense is None:
        return None

    # Only update fields the client actually sent
    update_fields = expense_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int, user_id: int) -> bool:
    expense = get_expense(db, expense_id, user_id)
    if expense is None:
        return False
    db.delete(expense)
    db.commit()
    return True
