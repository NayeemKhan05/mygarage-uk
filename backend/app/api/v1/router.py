from fastapi import APIRouter

from app.api.v1.routes import health, vehicles


api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["vehicles"],
)