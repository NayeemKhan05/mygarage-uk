from datetime import (
    datetime,
    timezone,
)
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
    get_optional_user,
)
from app.db.session import get_db
from app.models.user import User
from app.models.user_vehicle import UserVehicle
from app.models.vehicle import Vehicle
from app.models.vehicle_check_history import (
    VehicleCheckHistory,
)
from app.schemas.check_history import (
    VehicleCheckHistoryCreate,
    VehicleCheckHistoryRead,
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


OptionalUser = Annotated[
    User | None,
    Depends(get_optional_user),
]


def get_garage_vehicle_id(
    db: Session,
    user_id: int,
    registration: str,
) -> int | None:
    return db.scalar(
        select(Vehicle.id)
        .join(
            UserVehicle,
            UserVehicle.vehicle_id
            == Vehicle.id,
        )
        .where(
            UserVehicle.user_id
            == user_id,
            Vehicle.registration
            == registration,
        )
    )


def history_item_to_read(
    db: Session,
    user_id: int,
    item: VehicleCheckHistory,
) -> VehicleCheckHistoryRead:
    garage_vehicle_id = (
        get_garage_vehicle_id(
            db,
            user_id,
            item.registration,
        )
    )

    return VehicleCheckHistoryRead(
        id=item.id,
        registration=item.registration,
        make=item.make,
        model=item.model,
        fuel_type=item.fuel_type,
        colour=item.colour,
        year=item.year,
        first_checked_at=(
            item.first_checked_at
        ),
        last_checked_at=(
            item.last_checked_at
        ),
        check_count=item.check_count,
        in_garage=(
            garage_vehicle_id is not None
        ),
        garage_vehicle_id=(
            garage_vehicle_id
        ),
    )


@router.post(
    "/history",
    response_model=(
        VehicleCheckHistoryRead
        | None
    ),
)
def save_vehicle_check_history(
    payload: VehicleCheckHistoryCreate,
    db: DbSession,
    current_user: OptionalUser,
) -> VehicleCheckHistoryRead | None:
    # Anonymous lookups remain completely read-only.
    if current_user is None:
        return None

    existing = db.scalar(
        select(
            VehicleCheckHistory
        ).where(
            VehicleCheckHistory.user_id
            == current_user.id,
            VehicleCheckHistory.registration
            == payload.registration,
        )
    )

    now = datetime.now(
        timezone.utc
    )

    if existing is None:
        item = VehicleCheckHistory(
            user_id=current_user.id,
            registration=(
                payload.registration
            ),
            make=payload.make,
            model=payload.model,
            fuel_type=payload.fuel_type,
            colour=payload.colour,
            year=payload.year,
            first_checked_at=now,
            last_checked_at=now,
            check_count=1,
        )

        db.add(item)

    else:
        item = existing

        item.make = payload.make
        item.model = payload.model
        item.fuel_type = (
            payload.fuel_type
        )
        item.colour = payload.colour
        item.year = payload.year

        item.last_checked_at = now
        item.check_count += 1

    db.commit()
    db.refresh(item)

    return history_item_to_read(
        db,
        current_user.id,
        item,
    )


@router.get(
    "/history",
    response_model=list[
        VehicleCheckHistoryRead
    ],
)
def list_vehicle_check_history(
    db: DbSession,
    current_user: CurrentUser,
) -> list[VehicleCheckHistoryRead]:
    items = list(
        db.scalars(
            select(
                VehicleCheckHistory
            )
            .where(
                VehicleCheckHistory.user_id
                == current_user.id
            )
            .order_by(
                VehicleCheckHistory
                .last_checked_at
                .desc()
            )
        ).all()
    )

    if not items:
        return []

    registrations = [
        item.registration
        for item in items
    ]

    garage_rows = db.execute(
        select(
            Vehicle.registration,
            Vehicle.id,
        )
        .join(
            UserVehicle,
            UserVehicle.vehicle_id
            == Vehicle.id,
        )
        .where(
            UserVehicle.user_id
            == current_user.id,
            Vehicle.registration.in_(
                registrations
            ),
        )
    ).all()

    garage_by_registration = {
        registration: vehicle_id
        for (
            registration,
            vehicle_id,
        ) in garage_rows
    }

    return [
        VehicleCheckHistoryRead(
            id=item.id,
            registration=(
                item.registration
            ),
            make=item.make,
            model=item.model,
            fuel_type=item.fuel_type,
            colour=item.colour,
            year=item.year,
            first_checked_at=(
                item.first_checked_at
            ),
            last_checked_at=(
                item.last_checked_at
            ),
            check_count=(
                item.check_count
            ),
            in_garage=(
                item.registration
                in garage_by_registration
            ),
            garage_vehicle_id=(
                garage_by_registration.get(
                    item.registration
                )
            ),
        )
        for item in items
    ]


@router.delete(
    "/history/{check_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle_check_history_item(
    check_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    item = db.scalar(
        select(
            VehicleCheckHistory
        ).where(
            VehicleCheckHistory.id
            == check_id,
            VehicleCheckHistory.user_id
            == current_user.id,
        )
    )

    if item is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Check not found",
        )

    db.delete(item)
    db.commit()

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_vehicle_check_history(
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    db.execute(
        delete(
            VehicleCheckHistory
        ).where(
            VehicleCheckHistory.user_id
            == current_user.id
        )
    )

    db.commit()

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )