"""
Pydantic schemas define the "shape" of data going in and out of the API.

- ExpenseCreate: what the client must send to create an expense
- ExpenseUpdate: what the client may send to update an expense
- ExpenseOut:    what the API sends back to the client
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# The 10 default categories from the project spec
DEFAULT_CATEGORIES = {
    "Food", "Travel", "Shopping", "Bills", "Health",
    "Entertainment", "Education", "Subscriptions", "Rent", "Others"
}


class ExpenseBase(BaseModel):
    expense_date: date
    amount: Decimal = Field(..., gt=0, description="Must be greater than zero")
    category: str
    custom_category: Optional[str] = None
    note: Optional[str] = None

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: str) -> str:
        if v not in DEFAULT_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(DEFAULT_CATEGORIES)}"
            )
        return v


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    # All fields optional - user may only want to change one field
    expense_date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = None
    custom_category: Optional[str] = None
    note: Optional[str] = None

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEFAULT_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(DEFAULT_CATEGORIES)}"
            )
        return v


class ExpenseOut(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # allows Pydantic to read SQLAlchemy objects directly


class CategorySuggestionRequest(BaseModel):
    note: str
