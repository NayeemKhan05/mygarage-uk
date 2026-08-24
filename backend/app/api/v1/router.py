from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    check_history,
    health,
    maintenance,
    reminders,
    service_records,
    vehicle_checks,
    vehicles,
)


api_router = APIRouter()


api_router.include_router(
    health.router,
    tags=["health"],
)


api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)


api_router.include_router(
    vehicle_checks.router,
    prefix="/vehicle-checks",
    tags=["vehicle checks"],
)


api_router.include_router(
    check_history.router,
    prefix="/vehicle-checks",
    tags=["check history"],
)


api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["vehicles"],
)


api_router.include_router(
    service_records.router,
    prefix="/vehicles",
    tags=["service history"],
)


api_router.include_router(
    maintenance.router,
    prefix="/vehicles",
    tags=["maintenance"],
)


api_router.include_router(
    reminders.router,
    prefix="/reminders",
    tags=["reminders"],
)