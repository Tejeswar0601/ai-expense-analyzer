"""
SQLAlchemy model for the 'users' table.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, func
from backend.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
