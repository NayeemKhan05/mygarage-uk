from fastapi import APIRouter

from app.api.v1.routes import (
    health,
    vehicle_checks,
    vehicles,
)


api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    vehicle_checks.router,
    prefix="/vehicle-checks",
    tags=["vehicle checks"],
)

api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["vehicles"],
)