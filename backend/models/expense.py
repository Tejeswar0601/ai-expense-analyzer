"""
SQLAlchemy model for the 'expenses' table.

This class maps directly to the table we created in database/schema.sql.
SQLAlchemy uses this to translate Python objects <-> SQL rows.
"""

from sqlalchemy import Column, Integer, String, Date, DECIMAL, Text, TIMESTAMP, ForeignKey, func
from backend.database.connection import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    expense_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    custom_category = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
