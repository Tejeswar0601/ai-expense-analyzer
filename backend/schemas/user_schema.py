"""
Pydantic schemas for authentication: what the client sends to
register/login, and what the API sends back.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="At least 8 characters")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        # Emails are case-insensitive by convention - normalize so
        # "Test@Example.com" and "test@example.com" are the same
        # account, both when creating and when looking one up.
        return v.strip().lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResendOTPRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class DeleteAccountRequest(BaseModel):
    password: str
