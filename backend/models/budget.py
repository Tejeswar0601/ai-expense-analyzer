"""
SQLAlchemy model for the 'budgets' table.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, UniqueConstraint, func
from backend.database.connection import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category", "month_year", name="uq_budget_user_category_month"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)
    monthly_limit = Column(DECIMAL(10, 2), nullable=False)
    month_year = Column(String(7), nullable=False)  # 'YYYY-MM'
    created_at = Column(TIMESTAMP, server_default=func.now())
