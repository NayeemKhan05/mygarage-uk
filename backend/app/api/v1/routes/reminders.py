from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
)
from app.db.session import get_db
from app.models.reminder import (
    ReminderDismissal,
)
from app.models.user import User
from app.schemas.reminder import (
    ReminderDismissRequest,
    ReminderRead,
    ReminderSettingsRead,
    ReminderSettingsUpdate,
    ReminderSummaryRead,
)
from app.services.reminder_engine import (
    build_reminder_summary,
    build_user_reminders,
    get_or_create_reminder_settings,
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


@router.get(
    "",
    response_model=list[
        ReminderRead
    ],
)
def list_reminders(
    db: DbSession,
    current_user: CurrentUser,
) -> list[ReminderRead]:
    return build_user_reminders(
        db,
        current_user.id,
    )


@router.get(
    "/summary",
    response_model=(
        ReminderSummaryRead
    ),
)
def get_reminder_summary(
    db: DbSession,
    current_user: CurrentUser,
) -> ReminderSummaryRead:
    reminders = (
        build_user_reminders(
            db,
            current_user.id,
        )
    )

    return build_reminder_summary(
        reminders
    )


@router.get(
    "/settings",
    response_model=(
        ReminderSettingsRead
    ),
)
def get_reminder_settings(
    db: DbSession,
    current_user: CurrentUser,
):
    return (
        get_or_create_reminder_settings(
            db,
            current_user.id,
        )
    )


@router.put(
    "/settings",
    response_model=(
        ReminderSettingsRead
    ),
)
def update_reminder_settings(
    payload: ReminderSettingsUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    settings = (
        get_or_create_reminder_settings(
            db,
            current_user.id,
        )
    )

    changes = payload.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(
            settings,
            field,
            value,
        )

    db.commit()
    db.refresh(settings)

    return settings


@router.post(
    "/dismiss",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def dismiss_reminder(
    payload: ReminderDismissRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    reminders = (
        build_user_reminders(
            db,
            current_user.id,
            include_dismissed=True,
        )
    )

    valid_keys = {
        reminder.reminder_key
        for reminder in reminders
    }

    if (
        payload.reminder_key
        not in valid_keys
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Reminder not found"
            ),
        )

    existing = db.scalar(
        select(
            ReminderDismissal
        ).where(
            ReminderDismissal.user_id
            == current_user.id,
            ReminderDismissal.reminder_key
            == payload.reminder_key,
        )
    )

    if existing is None:
        db.add(
            ReminderDismissal(
                user_id=(
                    current_user.id
                ),
                reminder_key=(
                    payload.reminder_key
                ),
            )
        )

        db.commit()

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )


@router.delete(
    "/dismissals",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def restore_dismissed_reminders(
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    db.execute(
        delete(
            ReminderDismissal
        ).where(
            ReminderDismissal.user_id
            == current_user.id
        )
    )

    db.commit()

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )