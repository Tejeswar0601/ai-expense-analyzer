"""
API routes for authentication: register, login, email verification
(OTP), and account deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.api.deps import get_current_user
from backend.schemas.user_schema import (
    UserRegister, UserLogin, UserOut, Token,
    OTPVerifyRequest, ResendOTPRequest, DeleteAccountRequest,
)
from backend.services.auth_service import hash_password, verify_password, create_access_token
from backend.services import otp_service, account_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Best-effort: registration still succeeds even if the email
    # provider hiccups - the person can request a new code any time.
    otp_service.create_and_send_otp(db, user)

    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # Login is allowed before verification (a reminder banner nags
    # them instead of a hard block) - see is_verified in the response.
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=user)


@router.post("/verify-otp")
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email.")

    try:
        otp_service.verify_otp(db, user, payload.otp)
    except otp_service.OTPError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Email verified successfully.", "is_verified": True}


@router.post("/resend-otp")
def resend_otp(payload: ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email.")
    if user.is_verified:
        return {"message": "This account is already verified."}

    otp_service.create_and_send_otp(db, user)
    return {"message": "A new verification code has been sent."}


@router.delete("/account")
def delete_account(
    payload: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently deletes the logged-in user's account and all of their
    data (expenses, budgets, AI insights). Requires re-entering the
    password as a confirmation step, since this is irreversible.
    """
    if not verify_password(payload.password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password.")

    account_service.delete_account(db, current_user)
    return {"message": "Your account and all associated data have been permanently deleted."}
