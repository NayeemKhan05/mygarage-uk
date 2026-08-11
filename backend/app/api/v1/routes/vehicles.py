from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleRead


router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(payload: VehicleCreate, db: DbSession) -> Vehicle:
    vehicle = Vehicle(**payload.model_dump())

    db.add(vehicle)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this registration already exists",
        )

    db.refresh(vehicle)

    return vehicle


@router.get(
    "",
    response_model=list[VehicleRead],
)
def list_vehicles(db: DbSession) -> list[Vehicle]:
    statement = select(Vehicle).order_by(Vehicle.created_at.desc())

    return list(db.scalars(statement).all())


@router.get(
    "/{vehicle_id}",
    response_model=VehicleRead,
)
def get_vehicle(vehicle_id: int, db: DbSession) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)

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
def delete_vehicle(vehicle_id: int, db: DbSession) -> Response:
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    db.delete(vehicle)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)