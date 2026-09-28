"""
Thin wrapper around the FastAPI backend.

All Streamlit pages call functions here instead of using `requests`
directly - keeps HTTP details in one place, and if the API URL or
endpoint shapes change later, only this file needs updating.

Every request now attaches the logged-in user's JWT (read from
st.session_state) via _auth_headers(), since every backend route
except register/login requires authentication.
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _auth_headers() -> dict:
    token = st.session_state.get("access_token")
    if not token:
        raise RuntimeError("Not logged in.")
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------
# Authentication (no token needed for these two)
# ---------------------------------------------------------------------

def register(full_name: str, email: str, password: str) -> dict:
    response = requests.post(
        f"{API_URL}/api/auth/register",
        json={"full_name": full_name, "email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def verify_otp(email: str, otp: str) -> dict:
    response = requests.post(
        f"{API_URL}/api/auth/verify-otp",
        json={"email": email, "otp": otp},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def resend_otp(email: str) -> dict:
    response = requests.post(
        f"{API_URL}/api/auth/resend-otp",
        json={"email": email},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def delete_account(password: str) -> dict:
    response = requests.delete(
        f"{API_URL}/api/auth/account",
        json={"password": password},
        headers=_auth_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------
# Expenses (all require login)
# ---------------------------------------------------------------------

def add_expense(expense_data: dict) -> dict:
    response = requests.post(
        f"{API_URL}/api/expenses", json=expense_data, headers=_auth_headers(), timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_expenses(skip: int = 0, limit: int = 1000) -> list:
    response = requests.get(
        f"{API_URL}/api/expenses",
        params={"skip": skip, "limit": limit},
        headers=_auth_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_expense(expense_id: int) -> dict:
    response = requests.get(
        f"{API_URL}/api/expenses/{expense_id}", headers=_auth_headers(), timeout=10
    )
    response.raise_for_status()
    return response.json()


def update_expense(expense_id: int, expense_data: dict) -> dict:
    response = requests.put(
        f"{API_URL}/api/expenses/{expense_id}",
        json=expense_data,
        headers=_auth_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def delete_expense(expense_id: int) -> None:
    response = requests.delete(
        f"{API_URL}/api/expenses/{expense_id}", headers=_auth_headers(), timeout=10
    )
    response.raise_for_status()


def upload_expenses(file_bytes: bytes, filename: str, dry_run: bool = True) -> dict:
    """
    Send a CSV/XLSX file to the backend for validation (dry_run=True)
    or validation + import (dry_run=False).
    """
    files = {"file": (filename, file_bytes)}
    response = requests.post(
        f"{API_URL}/api/expenses/upload",
        files=files,
        params={"dry_run": dry_run},
        headers=_auth_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def suggest_category(note: str) -> dict:
    """Asks the backend for an ML-based category suggestion based on
    the note text, trained on this user's own past expenses."""
    response = requests.post(
        f"{API_URL}/api/expenses/suggest-category",
        json={"note": note},
        headers=_auth_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def scan_receipt(file_bytes: bytes, filename: str) -> dict:
    """Uploads a receipt image and gets back OCR text plus guessed
    amount/date/vendor - a suggestion only, never auto-saved."""
    files = {"file": (filename, file_bytes)}
    response = requests.post(
        f"{API_URL}/api/expenses/scan-receipt",
        files=files,
        headers=_auth_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------
# Reports (all require login)
# ---------------------------------------------------------------------

def get_monthly_report(year: int, month: int) -> dict:
    response = requests.get(
        f"{API_URL}/api/reports/{year}/{month}", headers=_auth_headers(), timeout=15
    )
    response.raise_for_status()
    return response.json()


def generate_ai_report(year: int, month: int) -> dict:
    """Calls the /generate endpoint, which computes stats AND asks the
    AI to explain them. Can take longer than a normal request since it
    hits the Groq API - using a generous timeout since occasional slow
    responses shouldn't look like a silent failure."""
    response = requests.post(
        f"{API_URL}/api/reports/{year}/{month}/generate",
        headers=_auth_headers(),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def get_forecast(year: int, month: int) -> dict:
    response = requests.get(
        f"{API_URL}/api/reports/{year}/{month}/forecast",
        headers=_auth_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def get_saved_insights(year: int, month: int):
    """Returns previously generated AI insights for this month, or
    None if nothing has been generated yet (no Groq call is made)."""
    response = requests.get(
        f"{API_URL}/api/reports/{year}/{month}/insights",
        headers=_auth_headers(),
        timeout=10,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def download_report_pdf(year: int, month: int) -> bytes:
    response = requests.get(
        f"{API_URL}/api/reports/{year}/{month}/pdf",
        headers=_auth_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.content


# ---------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------

def set_budget(category: str, monthly_limit: float, month_year: str) -> dict:
    response = requests.post(
        f"{API_URL}/api/budgets",
        json={"category": category, "monthly_limit": monthly_limit, "month_year": month_year},
        headers=_auth_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_budget_utilization(year: int, month: int) -> list:
    response = requests.get(
        f"{API_URL}/api/budgets/{year}/{month}", headers=_auth_headers(), timeout=10
    )
    response.raise_for_status()
    return response.json()


def delete_budget(budget_id: int) -> None:
    response = requests.delete(
        f"{API_URL}/api/budgets/{budget_id}", headers=_auth_headers(), timeout=10
    )
    response.raise_for_status()
