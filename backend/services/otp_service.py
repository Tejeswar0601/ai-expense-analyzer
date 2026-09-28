"""
Email OTP verification: generates a 6-digit code, emails it via
email_service, and verifies what the user types back against it.

Sending failures never block registration/login - the person can
just use "resend code" later. This matches the choice to let people
log in before verifying, with a reminder banner instead of a hard block.
"""

import random
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from backend.models.user import User
from backend.services import email_service

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10


class OTPError(Exception):
    pass


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=OTP_LENGTH))


def create_and_send_otp(db: Session, user: User) -> None:
    code = generate_otp()
    user.otp_code = code
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.commit()

    subject = "Your AI Expense Analyzer verification code"
    body = (
        f"Hi {user.full_name},\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code expires in {OTP_EXPIRY_MINUTES} minutes.\n\n"
        f"If you didn't request this, you can safely ignore this email."
    )

    try:
        email_service.send_email(user.email, subject, body)
    except email_service.EmailError:
        # Best-effort: don't let an email hiccup block registration/login.
        # The person can hit "Resend code" once email is working again.
        pass


def verify_otp(db: Session, user: User, submitted_code: str) -> None:
    if user.is_verified:
        return  # already verified, nothing to do

    if not user.otp_code or not user.otp_expires_at:
        raise OTPError("No verification code found. Please request a new one.")

    expires_at = user.otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        raise OTPError("This code has expired. Please request a new one.")

    if (submitted_code or "").strip() != user.otp_code:
        raise OTPError("Incorrect verification code.")

    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
