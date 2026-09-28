"""
Account deletion: permanently removes a user and all of their data.

Child tables (expenses, budgets, ai_insights) are deleted explicitly
before the user row itself, since the foreign keys don't cascade
automatically - this keeps the delete from failing on a constraint
violation and makes exactly what gets removed explicit and auditable.
"""

from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.expense import Expense
from backend.models.budget import Budget
from backend.models.ai_insight import AIInsight


def delete_account(db: Session, user: User) -> None:
    db.query(Expense).filter(Expense.user_id == user.id).delete()
    db.query(Budget).filter(Budget.user_id == user.id).delete()
    db.query(AIInsight).filter(AIInsight.user_id == user.id).delete()
    db.delete(user)
    db.commit()
