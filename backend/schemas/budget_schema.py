"""
Pydantic schemas for budgets.
"""

import re
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

DEFAULT_CATEGORIES = {
    "Food", "Travel", "Shopping", "Bills", "Health",
    "Entertainment", "Education", "Subscriptions", "Rent", "Others",
}

MONTH_YEAR_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class BudgetSet(BaseModel):
    category: str
    monthly_limit: Decimal = Field(..., gt=0)
    month_year: str = Field(..., description="Format: YYYY-MM, e.g. 2026-09")

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: str) -> str:
        if v not in DEFAULT_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(DEFAULT_CATEGORIES)}")
        return v

    @field_validator("month_year")
    @classmethod
    def month_year_format(cls, v: str) -> str:
        if not MONTH_YEAR_PATTERN.match(v):
            raise ValueError("month_year must be in 'YYYY-MM' format")
        return v


class BudgetUtilizationOut(BaseModel):
    id: int
    category: str
    monthly_limit: float
    spent: float
    remaining: float
    percent_used: float
    status: str
