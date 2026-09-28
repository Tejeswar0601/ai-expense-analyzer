"""
Authentication page: login and register, shown when the user has no
valid session. On success, stores the JWT and user info in
st.session_state so the rest of the app can use them.

After registering, an OTP verification box appears inline so the
person can immediately enter the code emailed to them - though
per the app's design, they can also skip this and log in right away
(a reminder banner nags them to verify from inside the app instead).
"""

import requests
import streamlit as st

from services.api_client import (
    login as api_login,
    register as api_register,
    verify_otp as api_verify_otp,
    resend_otp as api_resend_otp,
)
from components.icons import icon_heading


def _handle_login(email: str, password: str):
    try:
        result = api_login(email, password)
        st.session_state["access_token"] = result["access_token"]
        st.session_state["current_user"] = result["user"]
        st.rerun()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            st.error("Incorrect email or password.")
        else:
            st.error(f"Login failed: {e}")
    except Exception as e:
        st.error(f"Could not reach the server. Is FastAPI running? ({e})")


def _handle_register(full_name: str, email: str, password: str, confirm_password: str):
    if not full_name.strip():
        st.error("Please enter your name.")
        return
    if len(password) < 8:
        st.error("Password must be at least 8 characters.")
        return
    if password != confirm_password:
        st.error("Passwords do not match.")
        return

    try:
        api_register(full_name.strip(), email.strip(), password)
        st.session_state["pending_verification_email"] = email.strip()
        st.rerun()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 400:
            st.error("An account with this email already exists.")
        else:
            st.error(f"Registration failed: {e}")
    except Exception as e:
        st.error(f"Could not reach the server. Is FastAPI running? ({e})")


def _render_otp_box():
    pending_email = st.session_state.get("pending_verification_email")
    if not pending_email:
        return

    st.success("Account created! Check your email for a 6-digit verification code.")
    st.caption(f"Sent to {pending_email}")

    with st.form("otp_verify_form"):
        otp = st.text_input("Enter verification code", max_chars=6)
        col1, col2 = st.columns(2)
        verify_clicked = col1.form_submit_button("Verify")
        resend_clicked = col2.form_submit_button("Resend code")

    if verify_clicked:
        try:
            api_verify_otp(pending_email, otp)
            st.success("✅ Email verified! You can now log in below.")
            st.session_state.pop("pending_verification_email", None)
            st.rerun()
        except requests.exceptions.HTTPError as e:
            detail = e.response.json().get("detail", "Verification failed.") if e.response is not None else str(e)
            st.error(detail)
        except Exception as e:
            st.error(f"Could not reach the server: {e}")

    if resend_clicked:
        try:
            api_resend_otp(pending_email)
            st.info("A new code has been sent.")
        except Exception as e:
            st.error(f"Could not resend code: {e}")

    st.caption("You can also skip this for now and verify later from inside the app.")
    if st.button("Skip for now"):
        st.session_state.pop("pending_verification_email", None)
        st.rerun()


def render():
    st.markdown(icon_heading("logo", "Welcome to Expense Analyzer"), unsafe_allow_html=True)
    st.caption("Log in or create an account to start tracking your spending.")

    if st.session_state.get("pending_verification_email"):
        _render_otp_box()
        st.divider()

    tab_login, tab_register = st.tabs(["Log In", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
        if submitted:
            _handle_login(email.strip(), password)

    with tab_register:
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account")
        if submitted:
            _handle_register(full_name, email, password, confirm_password)
