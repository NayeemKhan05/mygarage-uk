from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.maintenance import MaintenanceItem
from app.models.user import User
from app.models.user_vehicle import UserVehicle
from app.schemas.maintenance import (
    MaintenanceItemCreate,
    MaintenanceItemRead,
    MaintenanceItemUpdate,
)
from app.services.maintenance_status import (
    get_latest_vehicle_mileage,
    maintenance_item_to_read,
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


def require_owned_vehicle(
    db: Session,
    user_id: int,
    vehicle_id: int,
) -> None:
    ownership = db.scalar(
        select(UserVehicle).where(
            UserVehicle.user_id
            == user_id,
            UserVehicle.vehicle_id
            == vehicle_id,
        )
    )

    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Vehicle not found "
                "in My Vehicles"
            ),
        )


def get_owned_maintenance_item(
    db: Session,
    user_id: int,
    vehicle_id: int,
    item_id: int,
) -> MaintenanceItem:
    item = db.scalar(
        select(MaintenanceItem).where(
            MaintenanceItem.id
            == item_id,
            MaintenanceItem.user_id
            == user_id,
            MaintenanceItem.vehicle_id
            == vehicle_id,
        )
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Maintenance item not found"
            ),
        )

    return item


@router.get(
    "/{vehicle_id}/maintenance",
    response_model=list[MaintenanceItemRead],
)
def list_maintenance_items(
    vehicle_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[MaintenanceItemRead]:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    items = db.scalars(
        select(MaintenanceItem)
        .where(
            MaintenanceItem.user_id
            == current_user.id,
            MaintenanceItem.vehicle_id
            == vehicle_id,
        )
        .order_by(
            MaintenanceItem.created_at.desc()
        )
    ).all()

    current_mileage = (
        get_latest_vehicle_mileage(
            db,
            vehicle_id,
        )
    )

    return [
        maintenance_item_to_read(
            item,
            current_mileage,
        )
        for item in items
    ]


@router.post(
    "/{vehicle_id}/maintenance",
    response_model=MaintenanceItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_item(
    vehicle_id: int,
    payload: MaintenanceItemCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> MaintenanceItemRead:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    item = MaintenanceItem(
        user_id=current_user.id,
        vehicle_id=vehicle_id,
        **payload.model_dump(),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    current_mileage = (
        get_latest_vehicle_mileage(
            db,
            vehicle_id,
        )
    )

    return maintenance_item_to_read(
        item,
        current_mileage,
    )


@router.put(
    "/{vehicle_id}/maintenance/{item_id}",
    response_model=MaintenanceItemRead,
)
def update_maintenance_item(
    vehicle_id: int,
    item_id: int,
    payload: MaintenanceItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> MaintenanceItemRead:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    item = get_owned_maintenance_item(
        db,
        current_user.id,
        vehicle_id,
        item_id,
    )

    changes = payload.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(
            item,
            field,
            value,
        )

    db.commit()
    db.refresh(item)

    current_mileage = (
        get_latest_vehicle_mileage(
            db,
            vehicle_id,
        )
    )

    return maintenance_item_to_read(
        item,
        current_mileage,
    )


@router.delete(
    "/{vehicle_id}/maintenance/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_maintenance_item(
    vehicle_id: int,
    item_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    item = get_owned_maintenance_item(
        db,
        current_user.id,
        vehicle_id,
        item_id,
    )

    db.delete(item)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )