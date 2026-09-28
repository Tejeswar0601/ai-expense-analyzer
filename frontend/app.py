"""
AI Expense Analyzer - Streamlit frontend entry point.

Run with (from the project root, ai-expense-analyzer/):
    streamlit run frontend/app.py
"""

import os
import sys

# Make sure "services" and "app_pages" are importable regardless of
# which directory `streamlit run` is launched from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import streamlit as st
from PIL import Image

from app_pages.add_expense import render as render_add_expense
from app_pages.expense_history import render as render_expense_history
from app_pages.upload_expenses import render as render_upload_expenses
from app_pages.dashboard import render as render_dashboard
from app_pages.monthly_report import render as render_monthly_report
from app_pages.budgets import render as render_budgets
from app_pages.auth import render as render_auth
from components.styles import inject_custom_css, render_logo_row
from services.api_client import verify_otp, resend_otp, delete_account

# Custom favicon (falls back to an emoji if the image is missing for
# any reason, so the app never breaks over a missing asset).
_ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "app_icon.png")
try:
    page_icon = Image.open(_ICON_PATH)
except Exception:
    page_icon = "💰"

st.set_page_config(
    page_title="AI Expense Analyzer",
    page_icon=page_icon,
    layout="wide",
)

inject_custom_css()

# --- Auth gate: nothing else renders until the user is logged in ---
if "access_token" not in st.session_state:
    render_auth()
    st.stop()

# IMPORTANT: dict order below defines which CSS icon each nav row gets
# (see components/styles.py - matched by nth-of-type). Keep this order
# in sync if you ever reorder the sidebar.
PAGES = {
    "Dashboard": render_dashboard,
    "Add Expense": render_add_expense,
    "Upload Expenses": render_upload_expenses,
    "Expense History": render_expense_history,
    "Monthly Report": render_monthly_report,
    "Budgets": render_budgets,
}

current_user = st.session_state.get("current_user", {})


def _render_verification_banner():
    """Reminder banner + inline OTP entry for unverified accounts.
    Never blocks access - the person can dismiss it and keep using
    the app, per the app's design choice."""
    with st.container():
        st.warning("⚠️ Your email isn't verified yet.")
        with st.expander("Verify now"):
            otp = st.text_input("Enter the 6-digit code sent to your email", key="nag_otp_input")
            c1, c2 = st.columns(2)
            if c1.button("Verify", key="nag_verify_btn"):
                try:
                    verify_otp(current_user["email"], otp)
                    st.session_state["current_user"]["is_verified"] = True
                    st.success("Verified!")
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    detail = e.response.json().get("detail", "Verification failed.") if e.response is not None else str(e)
                    st.error(detail)
                except Exception as e:
                    st.error(f"Could not reach the server: {e}")
            if c2.button("Resend code", key="nag_resend_btn"):
                try:
                    resend_otp(current_user["email"])
                    st.info("A new code has been sent.")
                except Exception as e:
                    st.error(f"Could not resend code: {e}")


def _render_delete_account_section():
    with st.expander("⚠️ Delete Account"):
        st.caption("This permanently deletes your account and ALL your data. This cannot be undone.")
        delete_password = st.text_input(
            "Confirm your password", type="password", key="delete_account_password"
        )
        confirm_checkbox = st.checkbox(
            "I understand this is permanent and cannot be undone.", key="delete_account_confirm"
        )
        if st.button("Permanently Delete My Account", disabled=not confirm_checkbox):
            try:
                delete_account(delete_password)
                st.session_state.clear()
                st.success("Your account has been deleted.")
                st.rerun()
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 401:
                    st.error("Incorrect password.")
                else:
                    st.error(f"Could not delete account: {e}")
            except Exception as e:
                st.error(f"Could not reach the server: {e}")


if not current_user.get("is_verified", True):
    _render_verification_banner()

with st.sidebar:
    render_logo_row("Expense Analyzer")
    st.caption("Track. Analyze. Understand your spending.")
    st.divider()
    selection = st.radio(
        "Navigate", list(PAGES.keys()), label_visibility="collapsed"
    )
    st.divider()
    st.caption(f"Logged in as **{current_user.get('full_name', 'User')}**")
    if st.button("Log Out"):
        st.session_state.clear()
        st.rerun()
    _render_delete_account_section()

render_fn = PAGES[selection]

if render_fn is None:
    st.title(selection)
    st.info("This page will be built in an upcoming phase.")
else:
    render_fn()
