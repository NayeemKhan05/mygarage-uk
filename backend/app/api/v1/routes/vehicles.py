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
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.api.dependencies.auth import (
    get_current_user,
)
from app.api.v1.dvsa import (
    fetch_dvsa_vehicle,
)
from app.db.session import get_db
from app.models.mot import MotTest
from app.models.user import User
from app.models.user_vehicle import (
    UserVehicle,
)
from app.models.vehicle import Vehicle
from app.schemas.mot import (
    MotHistoryRefreshResponse,
    MotTestRead,
)
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleImportResponse,
    VehicleLookupRequest,
    VehicleRead,
)
from app.services.dvsa_client import (
    DvsaClient,
    get_dvsa_client,
)
from app.services.mot_history import (
    save_mot_history,
)


router = APIRouter()


DbSession = Annotated[
    Session,
    Depends(get_db),
]


DvsaService = Annotated[
    DvsaClient,
    Depends(get_dvsa_client),
]


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


def get_owned_vehicle(
    db: Session,
    user_id: int,
    vehicle_id: int,
) -> Vehicle | None:
    return db.scalar(
        select(Vehicle)
        .join(
            UserVehicle,
            UserVehicle.vehicle_id
            == Vehicle.id,
        )
        .where(
            UserVehicle.user_id
            == user_id,
            Vehicle.id
            == vehicle_id,
        )
    )


def get_vehicle_link(
    db: Session,
    user_id: int,
    vehicle_id: int,
) -> UserVehicle | None:
    return db.scalar(
        select(UserVehicle).where(
            UserVehicle.user_id
            == user_id,
            UserVehicle.vehicle_id
            == vehicle_id,
        )
    )


@router.post(
    "",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    payload: VehicleCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Vehicle:
    existing_vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.registration
            == payload.registration
        )
    )

    if existing_vehicle is not None:
        existing_link = get_vehicle_link(
            db,
            current_user.id,
            existing_vehicle.id,
        )

        if existing_link is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This vehicle is already "
                    "in My Vehicles"
                ),
            )

        db.add(
            UserVehicle(
                user_id=current_user.id,
                vehicle_id=existing_vehicle.id,
            )
        )

        db.commit()

        return existing_vehicle

    vehicle = Vehicle(
        **payload.model_dump()
    )

    db.add(vehicle)

    try:
        db.flush()

        db.add(
            UserVehicle(
                user_id=current_user.id,
                vehicle_id=vehicle.id,
            )
        )

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This vehicle already exists"
            ),
        )

    db.refresh(vehicle)

    return vehicle


@router.post(
    "/import",
    response_model=VehicleImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_vehicle(
    payload: VehicleLookupRequest,
    db: DbSession,
    dvsa: DvsaService,
    current_user: CurrentUser,
) -> VehicleImportResponse:
    existing_vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.registration
            == payload.registration
        )
    )

    if existing_vehicle is not None:
        existing_link = get_vehicle_link(
            db,
            current_user.id,
            existing_vehicle.id,
        )

        if existing_link is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This vehicle is already "
                    "in My Vehicles"
                ),
            )

        db.add(
            UserVehicle(
                user_id=current_user.id,
                vehicle_id=existing_vehicle.id,
            )
        )

        db.commit()

        mot_test_count = db.scalar(
            select(
                func.count(
                    MotTest.id
                )
            ).where(
                MotTest.vehicle_id
                == existing_vehicle.id
            )
        )

        return VehicleImportResponse(
            vehicle=VehicleRead.model_validate(
                existing_vehicle
            ),
            mot_tests_found=(
                mot_test_count or 0
            ),
            mot_tests_saved=0,
        )

    dvsa_vehicle = fetch_dvsa_vehicle(
        dvsa,
        payload.registration,
    )

    if (
        not dvsa_vehicle.make
        or not dvsa_vehicle.model
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "DVSA returned incomplete "
                "vehicle data"
            ),
        )

    vehicle = Vehicle(
        registration=payload.registration,
        make=dvsa_vehicle.make,
        model=dvsa_vehicle.model,
        fuel_type=dvsa_vehicle.fuel_type,
        engine_size=dvsa_vehicle.engine_size,
        colour=dvsa_vehicle.primary_colour,
        year=dvsa_vehicle.year,
    )

    db.add(vehicle)

    try:
        # The MOT records need the vehicle ID.
        db.flush()

        mot_tests_saved = save_mot_history(
            db,
            vehicle,
            dvsa_vehicle.mot_tests,
        )

        db.add(
            UserVehicle(
                user_id=current_user.id,
                vehicle_id=vehicle.id,
            )
        )

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Could not add this vehicle "
                "to My Vehicles"
            ),
        )

    db.refresh(vehicle)

    return VehicleImportResponse(
        vehicle=VehicleRead.model_validate(
            vehicle
        ),
        mot_tests_found=len(
            dvsa_vehicle.mot_tests
        ),
        mot_tests_saved=mot_tests_saved,
    )


@router.get(
    "",
    response_model=list[VehicleRead],
)
def list_vehicles(
    db: DbSession,
    current_user: CurrentUser,
) -> list[Vehicle]:
    statement = (
        select(Vehicle)
        .join(
            UserVehicle,
            UserVehicle.vehicle_id
            == Vehicle.id,
        )
        .where(
            UserVehicle.user_id
            == current_user.id
        )
        .order_by(
            UserVehicle.added_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


@router.get(
    "/{vehicle_id}/mot-history",
    response_model=list[MotTestRead],
)
def get_vehicle_mot_history(
    vehicle_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[MotTest]:
    vehicle = get_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Vehicle not found "
                "in My Vehicles"
            ),
        )

    statement = (
        select(MotTest)
        .options(
            selectinload(
                MotTest.defects
            )
        )
        .where(
            MotTest.vehicle_id
            == vehicle_id
        )
        .order_by(
            MotTest.completed_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


@router.post(
    "/{vehicle_id}/mot-history/refresh",
    response_model=MotHistoryRefreshResponse,
)
def refresh_vehicle_mot_history(
    vehicle_id: int,
    db: DbSession,
    dvsa: DvsaService,
    current_user: CurrentUser,
) -> MotHistoryRefreshResponse:
    vehicle = get_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Vehicle not found "
                "in My Vehicles"
            ),
        )

    dvsa_vehicle = fetch_dvsa_vehicle(
        dvsa,
        vehicle.registration,
    )

    mot_tests_saved = save_mot_history(
        db,
        vehicle,
        dvsa_vehicle.mot_tests,
    )

    db.commit()

    return MotHistoryRefreshResponse(
        vehicle_id=vehicle.id,
        registration=vehicle.registration,
        mot_tests_found=len(
            dvsa_vehicle.mot_tests
        ),
        mot_tests_saved=mot_tests_saved,
    )


@router.get(
    "/{vehicle_id}",
    response_model=VehicleRead,
)
def get_vehicle(
    vehicle_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Vehicle:
    vehicle = get_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Vehicle not found "
                "in My Vehicles"
            ),
        )

    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(
    vehicle_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    link = get_vehicle_link(
        db,
        current_user.id,
        vehicle_id,
    )

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Vehicle not found "
                "in My Vehicles"
            ),
        )

    # Removing a car only removes it from this user's collection.
    # The shared vehicle and MOT records can still be used elsewhere.
    db.delete(link)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )