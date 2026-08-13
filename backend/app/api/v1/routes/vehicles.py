from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.api.v1.dvsa import fetch_dvsa_vehicle
from app.db.session import get_db
from app.models.mot import MotTest
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


@router.post(
    "",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    payload: VehicleCreate,
    db: DbSession,
) -> Vehicle:
    vehicle = Vehicle(
        **payload.model_dump()
    )

    db.add(vehicle)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A vehicle with this registration "
                "already exists"
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
) -> VehicleImportResponse:
    existing_vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.registration
            == payload.registration
        )
    )

    if existing_vehicle is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A vehicle with this registration "
                "already exists"
            ),
        )

    dvsa_vehicle = fetch_dvsa_vehicle(
        dvsa,
        payload.registration,
    )

    if not dvsa_vehicle.make or not dvsa_vehicle.model:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="DVSA returned incomplete vehicle data",
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
        # We need the vehicle ID before its MOT tests can reference it.
        db.flush()

        mot_tests_saved = save_mot_history(
            db,
            vehicle,
            dvsa_vehicle.mot_tests,
        )

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A vehicle with this registration "
                "already exists"
            ),
        )

    db.refresh(vehicle)

    return VehicleImportResponse(
        vehicle=VehicleRead.model_validate(vehicle),
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
) -> list[Vehicle]:
    statement = select(Vehicle).order_by(
        Vehicle.created_at.desc()
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/{vehicle_id}/mot-history",
    response_model=list[MotTestRead],
)
def get_vehicle_mot_history(
    vehicle_id: int,
    db: DbSession,
) -> list[MotTest]:
    vehicle = db.get(
        Vehicle,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    statement = (
        select(MotTest)
        .options(
            selectinload(MotTest.defects)
        )
        .where(
            MotTest.vehicle_id == vehicle_id
        )
        .order_by(
            MotTest.completed_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


@router.post(
    "/{vehicle_id}/mot-history/refresh",
    response_model=MotHistoryRefreshResponse,
)
def refresh_vehicle_mot_history(
    vehicle_id: int,
    db: DbSession,
    dvsa: DvsaService,
) -> MotHistoryRefreshResponse:
    vehicle = db.get(
        Vehicle,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
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
) -> Vehicle:
    vehicle = db.get(
        Vehicle,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(
    vehicle_id: int,
    db: DbSession,
) -> Response:
    vehicle = db.get(
        Vehicle,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    db.delete(vehicle)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )