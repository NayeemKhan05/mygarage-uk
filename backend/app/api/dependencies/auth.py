from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    InvalidAccessTokenError,
    decode_access_token,
)
from app.db.session import get_db
from app.models.user import User


DbSession = Annotated[
    Session,
    Depends(get_db),
]

# For routes that require login
def get_current_user(
    db: DbSession,
    access_token: Annotated[
        str | None,
        Cookie(
            alias=settings.auth_cookie_name
        ),
    ] = None,
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        user_id = decode_access_token(
            access_token
        )
    except InvalidAccessTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired login",
        )

    user = db.get(
        User,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    return user

# Lets the homepage to check MOTs anonymously.
def get_optional_user(
    db: DbSession,
    access_token: Annotated[
        str | None,
        Cookie(
            alias=settings.auth_cookie_name
        ),
    ] = None,
) -> User | None:
    if not access_token:
        return None

    try:
        user_id = decode_access_token(
            access_token
        )
    except InvalidAccessTokenError:
        return None

    return db.get(
        User,
        user_id,
    )