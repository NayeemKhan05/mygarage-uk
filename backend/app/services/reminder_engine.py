from datetime import (
    date,
    datetime,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.maintenance import (
    MaintenanceItem,
)
from app.models.mot import MotTest
from app.models.reminder import (
    ReminderDismissal,
    ReminderSettings,
)
from app.models.user_vehicle import UserVehicle
from app.models.vehicle import Vehicle
from app.schemas.reminder import (
    ReminderRead,
    ReminderSummaryRead,
)
from app.services.maintenance_status import (
    get_latest_vehicle_mileage,
)


def get_or_create_reminder_settings(
    db: Session,
    user_id: int,
) -> ReminderSettings:
    settings = db.get(
        ReminderSettings,
        user_id,
    )

    if settings is not None:
        return settings

    settings = ReminderSettings(
        user_id=user_id,
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings


def _normalise_date(
    value: date | datetime | None,
) -> date | None:
    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value.date()

    return value


def _vehicle_name(
    vehicle: Vehicle,
) -> tuple[
    str | None,
    str | None,
]:
    return (
        vehicle.make,
        vehicle.model,
    )


def _latest_mot_expiry(
    db: Session,
    vehicle_id: int,
) -> date | None:
    expiry = db.scalar(
        select(
            MotTest.expiry_date
        )
        .where(
            MotTest.vehicle_id
            == vehicle_id,
            MotTest.expiry_date.is_not(
                None
            ),
        )
        .order_by(
            MotTest.completed_at.desc()
        )
        .limit(1)
    )

    return _normalise_date(
        expiry
    )


def _build_mot_reminder(
    vehicle: Vehicle,
    expiry_date: date,
    due_soon_days: int,
) -> ReminderRead | None:
    today = date.today()

    days_remaining = (
        expiry_date
        - today
    ).days

    if (
        days_remaining
        > due_soon_days
    ):
        return None

    if days_remaining < 0:
        overdue_days = abs(
            days_remaining
        )

        severity = "urgent"

        title = "MOT expired"

        message = (
            f"MOT expired "
            f"{overdue_days} "
            f"{'day' if overdue_days == 1 else 'days'} ago."
        )

    elif days_remaining == 0:
        severity = "urgent"

        title = "MOT expires today"

        message = (
            "This vehicle's MOT expires today."
        )

    else:
        severity = "warning"

        title = "MOT due soon"

        message = (
            f"MOT expires in "
            f"{days_remaining} "
            f"{'day' if days_remaining == 1 else 'days'}."
        )

    make, model = (
        _vehicle_name(
            vehicle
        )
    )

    return ReminderRead(
        reminder_key=(
            f"mot:"
            f"{vehicle.id}:"
            f"{expiry_date.isoformat()}"
        ),
        kind="mot",
        severity=severity,
        title=title,
        message=message,
        vehicle_id=vehicle.id,
        registration=(
            vehicle.registration
        ),
        make=make,
        model=model,
        due_date=expiry_date,
        due_mileage=None,
        current_mileage=None,
        action_href=(
            f"/vehicles/{vehicle.id}"
        ),
    )


def _build_maintenance_reminder(
    vehicle: Vehicle,
    item: MaintenanceItem,
    current_mileage: int | None,
    due_soon_days: int,
    due_soon_miles: int,
) -> ReminderRead | None:
    today = date.today()

    urgent_reasons: list[str] = []
    warning_reasons: list[str] = []

    if (
        item.next_due_date
        is not None
    ):
        days_remaining = (
            item.next_due_date
            - today
        ).days

        if days_remaining < 0:
            overdue_days = abs(
                days_remaining
            )

            urgent_reasons.append(
                (
                    f"overdue by "
                    f"{overdue_days} "
                    f"{'day' if overdue_days == 1 else 'days'}"
                )
            )

        elif days_remaining == 0:
            urgent_reasons.append(
                "due today"
            )

        elif (
            days_remaining
            <= due_soon_days
        ):
            warning_reasons.append(
                (
                    f"due in "
                    f"{days_remaining} "
                    f"{'day' if days_remaining == 1 else 'days'}"
                )
            )

    if (
        item.next_due_mileage
        is not None
        and current_mileage
        is not None
    ):
        miles_remaining = (
            item.next_due_mileage
            - current_mileage
        )

        if miles_remaining < 0:
            urgent_reasons.append(
                (
                    f"overdue by "
                    f"{abs(miles_remaining):,} miles"
                )
            )

        elif miles_remaining == 0:
            urgent_reasons.append(
                "due at the current mileage"
            )

        elif (
            miles_remaining
            <= due_soon_miles
        ):
            warning_reasons.append(
                (
                    f"due in "
                    f"{miles_remaining:,} miles"
                )
            )

    if urgent_reasons:
        severity = "urgent"

        message = (
            f"{item.name} is "
            + " and ".join(
                urgent_reasons
            )
            + "."
        )

    elif warning_reasons:
        severity = "warning"

        message = (
            f"{item.name} is "
            + " and ".join(
                warning_reasons
            )
            + "."
        )

    else:
        return None

    make, model = (
        _vehicle_name(
            vehicle
        )
    )

    date_key = (
        item.next_due_date.isoformat()
        if item.next_due_date
        else "-"
    )

    mileage_key = (
        str(
            item.next_due_mileage
        )
        if (
            item.next_due_mileage
            is not None
        )
        else "-"
    )

    return ReminderRead(
        reminder_key=(
            f"maintenance:"
            f"{item.id}:"
            f"{date_key}:"
            f"{mileage_key}"
        ),
        kind="maintenance",
        severity=severity,
        title=item.name,
        message=message,
        vehicle_id=vehicle.id,
        registration=(
            vehicle.registration
        ),
        make=make,
        model=model,
        due_date=(
            item.next_due_date
        ),
        due_mileage=(
            item.next_due_mileage
        ),
        current_mileage=(
            current_mileage
        ),
        action_href=(
            f"/vehicles/{vehicle.id}"
        ),
    )


def build_user_reminders(
    db: Session,
    user_id: int,
    include_dismissed: bool = False,
) -> list[ReminderRead]:
    settings = (
        get_or_create_reminder_settings(
            db,
            user_id,
        )
    )

    dismissed_keys: set[str] = set()

    if not include_dismissed:
        dismissed_keys = set(
            db.scalars(
                select(
                    ReminderDismissal.reminder_key
                ).where(
                    ReminderDismissal.user_id
                    == user_id
                )
            ).all()
        )

    vehicles = list(
        db.scalars(
            select(Vehicle)
            .join(
                UserVehicle,
                UserVehicle.vehicle_id
                == Vehicle.id,
            )
            .where(
                UserVehicle.user_id
                == user_id
            )
            .order_by(
                Vehicle.registration
            )
        ).all()
    )

    reminders: list[
        ReminderRead
    ] = []

    for vehicle in vehicles:
        if settings.mot_enabled:
            expiry_date = (
                _latest_mot_expiry(
                    db,
                    vehicle.id,
                )
            )

            if expiry_date:
                reminder = (
                    _build_mot_reminder(
                        vehicle,
                        expiry_date,
                        settings.due_soon_days,
                    )
                )

                if (
                    reminder
                    and (
                        include_dismissed
                        or reminder.reminder_key
                        not in dismissed_keys
                    )
                ):
                    reminders.append(
                        reminder
                    )

        if (
            settings.maintenance_enabled
        ):
            current_mileage = (
                get_latest_vehicle_mileage(
                    db,
                    vehicle.id,
                )
            )

            maintenance_items = list(
                db.scalars(
                    select(
                        MaintenanceItem
                    )
                    .where(
                        MaintenanceItem.user_id
                        == user_id,
                        MaintenanceItem.vehicle_id
                        == vehicle.id,
                    )
                    .order_by(
                        MaintenanceItem.created_at
                    )
                ).all()
            )

            for item in maintenance_items:
                reminder = (
                    _build_maintenance_reminder(
                        vehicle,
                        item,
                        current_mileage,
                        settings.due_soon_days,
                        settings.due_soon_miles,
                    )
                )

                if (
                    reminder
                    and (
                        include_dismissed
                        or reminder.reminder_key
                        not in dismissed_keys
                    )
                ):
                    reminders.append(
                        reminder
                    )

    severity_order = {
        "urgent": 0,
        "warning": 1,
    }

    reminders.sort(
        key=lambda reminder: (
            severity_order[
                reminder.severity
            ],
            reminder.due_date
            or date.max,
            reminder.registration,
            reminder.title,
        )
    )

    return reminders


def build_reminder_summary(
    reminders: list[
        ReminderRead
    ],
) -> ReminderSummaryRead:
    return ReminderSummaryRead(
        total=len(
            reminders
        ),
        urgent=sum(
            reminder.severity
            == "urgent"
            for reminder in reminders
        ),
        warning=sum(
            reminder.severity
            == "warning"
            for reminder in reminders
        ),
        mot=sum(
            reminder.kind
            == "mot"
            for reminder in reminders
        ),
        maintenance=sum(
            reminder.kind
            == "maintenance"
            for reminder in reminders
        ),
    )