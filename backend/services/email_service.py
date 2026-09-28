"""
Sends transactional email via Gmail SMTP.

Sending is isolated in this one function (send_email) so other
services - like otp_service - can be unit-tested without actually
sending real email over the network.
"""

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM") or SMTP_USER


class EmailError(Exception):
    pass


def send_email(to_address: str, subject: str, body: str) -> None:
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
