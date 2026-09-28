"""
Reusable FastAPI dependency: extracts and validates the JWT from the
Authorization header, and loads the corresponding User from the DB.

Use it on any endpoint that should require login:
    current_user: User = Depends(get_current_user)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.services.auth_service import decode_access_token, TokenError

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise unauthorized

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise unauthorized

    return user
