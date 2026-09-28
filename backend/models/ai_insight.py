"""
SQLAlchemy model for the 'ai_insights' table.
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey, func
from backend.database.connection import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month_year = Column(String(7), nullable=False)
    insight_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(4, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
