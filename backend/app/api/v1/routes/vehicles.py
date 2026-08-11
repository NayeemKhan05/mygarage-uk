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
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleImportRequest,
    VehicleImportResponse,
    VehicleRead,
)
from app.services.dvsa_client import (
    DvsaAuthenticationError,
    DvsaBadRequestError,
    DvsaClient,
    DvsaConfigurationError,
    DvsaError,
    DvsaRateLimitError,
    DvsaUnavailableError,
    DvsaVehicleNotFoundError,
    get_dvsa_client,
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
    payload: VehicleImportRequest,
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

    try:
        dvsa_vehicle = (
            dvsa.get_vehicle_by_registration(
                payload.registration
            )
        )

    except DvsaBadRequestError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DVSA rejected this registration",
        )

    except DvsaVehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in DVSA records",
        )

    except DvsaConfigurationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DVSA integration is not configured",
        )

    except DvsaRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "DVSA is temporarily rate limiting requests"
            ),
        )

    except (
        DvsaAuthenticationError,
        DvsaUnavailableError,
        DvsaError,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Could not retrieve vehicle data from DVSA"
            ),
        )

    if not dvsa_vehicle.make or not dvsa_vehicle.model:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="DVSA returned incomplete vehicle data",
        )

    vehicle_date = (
        dvsa_vehicle.manufacture_date
        or dvsa_vehicle.first_used_date
        or dvsa_vehicle.registration_date
    )

    vehicle = Vehicle(
        registration=payload.registration,
        make=dvsa_vehicle.make,
        model=dvsa_vehicle.model,
        fuel_type=dvsa_vehicle.fuel_type,
        engine_size=dvsa_vehicle.engine_size,
        colour=dvsa_vehicle.primary_colour,
        year=(
            vehicle_date.year
            if vehicle_date
            else None
        ),
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

    return VehicleImportResponse(
        vehicle=VehicleRead.model_validate(vehicle),
        mot_tests_found=len(
            dvsa_vehicle.mot_tests
        ),
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