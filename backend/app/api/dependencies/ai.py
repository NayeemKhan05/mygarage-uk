from typing import (
    Annotated,
)

from fastapi import (
    Depends,
)

from app.services.ai_provider import (
    OllamaProvider,
)
from app.services.ai_vehicle_service import (
    VehicleAiService,
)


def get_ai_service(
) -> VehicleAiService:
    return VehicleAiService(
        provider=(
            OllamaProvider()
        )
    )


AiService = Annotated[
    VehicleAiService,
    Depends(
        get_ai_service
    ),
]