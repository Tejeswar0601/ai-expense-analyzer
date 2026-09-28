"""
Sends transactional email.

Two delivery paths, chosen automatically:
1. Brevo HTTPS API - used when BREVO_API_KEY is set (production).
   Needed because free Render web services block outbound SMTP
   ports (25/465/587), but can't block HTTPS on port 443.
2. Gmail SMTP - used otherwise (local development).

Sending is isolated in send_email() so other services (otp_service)
can be unit-tested without sending real email.
"""

import os
import smtplib
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM") or SMTP_USER


class EmailError(Exception):
    pass


def _send_via_brevo(to_address: str, subject: str, body: str) -> None:
    if not SMTP_FROM:
        raise EmailError("SMTP_FROM must be set to your verified Brevo sender address.")

    payload = {
        "sender": {"name": "AI Expense Analyzer", "email": SMTP_FROM},
        "to": [{"email": to_address}],
        "subject": subject,
        "textContent": body,
    }
    headers = {
        "api-key": BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }
    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise EmailError(f"Could not reach Brevo: {e}")

    if response.status_code >= 300:
        raise EmailError(f"Brevo rejected the email ({response.status_code}): {response.text}")


def _send_via_smtp(to_address: str, subject: str, body: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        raise EmailError(
            "Email is not configured. Set SMTP_USER and SMTP_PASSWORD in your .env file."
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_address

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [to_address], msg.as_string())
    except Exception as e:
        raise EmailError(f"Could not send email: {e}")


def send_email(to_address: str, subject: str, body: str) -> None:
    if BREVO_API_KEY:
        _send_via_brevo(to_address, subject, body)
    else:
        _send_via_smtp(to_address, subject, body)
