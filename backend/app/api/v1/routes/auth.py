from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.models.user_vehicle import UserVehicle
from app.models.vehicle import Vehicle
from app.schemas.auth import (
    UserLogin,
    UserRead,
    UserRegister,
)


router = APIRouter()


DbSession = Annotated[
    Session,
    Depends(get_db),
]

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


def set_auth_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=(
            settings.auth_token_expire_minutes
            * 60
        ),
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    response: Response,
    db: DbSession,
) -> User:
    email = str(
        payload.email
    ).lower()

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email "
                "already exists"
            ),
        )

    user_count = db.scalar(
        select(
            func.count(User.id)
        )
    )

    is_first_user = (
        user_count == 0
    )

    user = User(
        email=email,
        password_hash=hash_password(
            payload.password
        ),
    )

    db.add(user)

    try:
        db.flush()

        # Keep the cars we created before user accounts existed.
        # The first registered account takes ownership of them.
        if is_first_user:
            existing_vehicle_ids = (
                db.scalars(
                    select(
                        Vehicle.id
                    )
                ).all()
            )

            for vehicle_id in existing_vehicle_ids:
                db.add(
                    UserVehicle(
                        user_id=user.id,
                        vehicle_id=vehicle_id,
                    )
                )

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email "
                "already exists"
            ),
        )

    db.refresh(user)

    token = create_access_token(
        user.id
    )

    set_auth_cookie(
        response,
        token,
    )

    return user


@router.post(
    "/login",
    response_model=UserRead,
)
def login(
    payload: UserLogin,
    response: Response,
    db: DbSession,
) -> User:
    email = str(
        payload.email
    ).lower()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if (
        user is None
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(
        user.id
    )

    set_auth_cookie(
        response,
        token,
    )

    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        secure=settings.auth_cookie_secure,
        httponly=True,
        samesite="lax",
    )


@router.get(
    "/me",
    response_model=UserRead,
)
def me(
    current_user: CurrentUser,
) -> User:
    return current_user