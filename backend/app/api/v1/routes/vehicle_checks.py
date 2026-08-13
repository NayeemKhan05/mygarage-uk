from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dvsa import fetch_dvsa_vehicle
from app.db.session import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    VehicleCheckResponse,
    VehicleLookupRequest,
)
from app.services.dvsa_client import (
    DvsaClient,
    get_dvsa_client,
)
from app.services.mot_history import (
    dvsa_mot_test_to_read,
    sort_dvsa_mot_tests,
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
    response_model=VehicleCheckResponse,
    status_code=status.HTTP_200_OK,
)
def check_vehicle(
    payload: VehicleLookupRequest,
    db: DbSession,
    dvsa: DvsaService,
) -> VehicleCheckResponse:
    dvsa_vehicle = fetch_dvsa_vehicle(
        dvsa,
        payload.registration,
    )

    if not dvsa_vehicle.make or not dvsa_vehicle.model:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="DVSA returned incomplete vehicle data",
        )

    existing_vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.registration
            == payload.registration
        )
    )

    mot_tests = [
        dvsa_mot_test_to_read(test)
        for test in sort_dvsa_mot_tests(
            dvsa_vehicle.mot_tests
        )
    ]

    return VehicleCheckResponse(
        registration=payload.registration,
        make=dvsa_vehicle.make,
        model=dvsa_vehicle.model,
        fuel_type=dvsa_vehicle.fuel_type,
        engine_size=dvsa_vehicle.engine_size,
        colour=dvsa_vehicle.primary_colour,
        year=dvsa_vehicle.year,
        mot_tests_found=len(mot_tests),
        mot_tests=mot_tests,
        in_garage=existing_vehicle is not None,
        garage_vehicle_id=(
            existing_vehicle.id
            if existing_vehicle
            else None
        ),
    )