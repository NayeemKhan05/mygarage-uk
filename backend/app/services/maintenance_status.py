from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.maintenance import MaintenanceItem
from app.models.mot import MotTest
from app.schemas.maintenance import MaintenanceItemRead


DUE_SOON_DAYS = 30
DUE_SOON_MILES = 1000


def get_latest_vehicle_mileage(
    db: Session,
    vehicle_id: int,
) -> int | None:
    mileage = db.scalar(
        select(
            MotTest.odometer_value
        )
        .where(
            MotTest.vehicle_id
            == vehicle_id,
            MotTest.odometer_value.is_not(
                None
            ),
        )
        .order_by(
            MotTest.completed_at.desc()
        )
        .limit(1)
    )

    if mileage is None:
        return None

    return int(
        mileage
    )


def maintenance_item_to_read(
    item: MaintenanceItem,
    current_mileage: int | None,
) -> MaintenanceItemRead:
    today = date.today()

    overdue_reasons: list[str] = []
    due_soon_reasons: list[str] = []
    future_reasons: list[str] = []

    if item.next_due_date:
        days_remaining = (
            item.next_due_date
            - today
        ).days

        if days_remaining < 0:
            overdue_reasons.append(
                (
                    f"Overdue by "
                    f"{abs(days_remaining)} "
                    f"{'day' if abs(days_remaining) == 1 else 'days'}"
                )
            )

        elif days_remaining <= DUE_SOON_DAYS:
            due_soon_reasons.append(
                (
                    f"Due in "
                    f"{days_remaining} "
                    f"{'day' if days_remaining == 1 else 'days'}"
                )
            )

        else:
            future_reasons.append(
                (
                    f"Due in "
                    f"{days_remaining} days"
                )
            )

    if item.next_due_mileage is not None:
        if current_mileage is None:
            future_reasons.append(
                (
                    "Due at "
                    f"{item.next_due_mileage:,} mi"
                )
            )

        else:
            miles_remaining = (
                item.next_due_mileage
                - current_mileage
            )

            if miles_remaining < 0:
                overdue_reasons.append(
                    (
                        f"Overdue by "
                        f"{abs(miles_remaining):,} mi"
                    )
                )

            elif miles_remaining <= DUE_SOON_MILES:
                due_soon_reasons.append(
                    (
                        f"Due in "
                        f"{miles_remaining:,} mi"
                    )
                )

            else:
                future_reasons.append(
                    (
                        f"Due in "
                        f"{miles_remaining:,} mi"
                    )
                )

    if overdue_reasons:
        status = "overdue"
        status_reason = " · ".join(
            overdue_reasons
        )

    elif due_soon_reasons:
        status = "due_soon"
        status_reason = " · ".join(
            due_soon_reasons
        )

    elif future_reasons:
        status = "good"
        status_reason = " · ".join(
            future_reasons
        )

    else:
        status = "unknown"
        status_reason = (
            "No next due date or mileage set"
        )

    return MaintenanceItemRead(
        id=item.id,
        vehicle_id=item.vehicle_id,
        name=item.name,
        category=item.category,
        last_completed_date=(
            item.last_completed_date
        ),
        last_completed_mileage=(
            item.last_completed_mileage
        ),
        next_due_date=(
            item.next_due_date
        ),
        next_due_mileage=(
            item.next_due_mileage
        ),
        notes=item.notes,
        status=status,
        status_reason=status_reason,
        current_mileage=current_mileage,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )