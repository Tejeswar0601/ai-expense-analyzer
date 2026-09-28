from datetime import datetime, timedelta, timezone

import pytest

from backend.models.user import User
from backend.services import otp_service, email_service


def test_generate_otp_is_six_digits():
    code = otp_service.generate_otp()
    assert len(code) == 6
    assert code.isdigit()


def test_create_and_send_otp_then_verify(db_session, monkeypatch):
    sent = []
    monkeypatch.setattr(
        email_service, "send_email",
        lambda to, subject, body: sent.append((to, subject, body)),
    )

    test_user = User(full_name="OTP Test", email="otp_pytest@example.com", password_hash="x", is_verified=False)
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    otp_service.create_and_send_otp(db_session, test_user)
    assert len(sent) == 1
    code = test_user.otp_code
    assert code in sent[0][2]  # the code appears in the email body

    with pytest.raises(otp_service.OTPError):
        otp_service.verify_otp(db_session, test_user, "000000")

    otp_service.verify_otp(db_session, test_user, code)
    assert test_user.is_verified is True
    assert test_user.otp_code is None


def test_expired_otp_rejected(db_session):
    test_user = User(
        full_name="Expired", email="otp_expired_pytest@example.com", password_hash="x", is_verified=False
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    test_user.otp_code = "123456"
    test_user.otp_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    with pytest.raises(otp_service.OTPError):
        otp_service.verify_otp(db_session, test_user, "123456")


def test_already_verified_user_is_a_safe_noop(db_session):
    test_user = User(
        full_name="AlreadyV", email="already_verified_pytest@example.com", password_hash="x", is_verified=True
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    otp_service.verify_otp(db_session, test_user, "anything")  # must not raise
