"""
FastAPI application entry point.

Run with (from the project root, ai-expense-analyzer/):
    uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from backend.database.connection import Base, engine
from backend.api import auth, expenses, reports, budgets

# Import models so SQLAlchemy's Base.metadata knows about every table
# before create_all runs below.
from backend.models import user, expense, budget, ai_insight  # noqa: F401

from fastapi.middleware.cors import CORSMiddleware

# Create all tables that don't already exist (safe to run repeatedly -
# it won't touch tables you already created manually)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Expense Analyzer API",
    description="Backend API for tracking and analyzing personal expenses",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your exact Streamlit URL once you have it
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(budgets.router)


@app.get("/")
def root():
    return {"message": "AI Expense Analyzer API is running"}
