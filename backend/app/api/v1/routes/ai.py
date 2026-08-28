from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.api.dependencies.ai import (
    AiService,
)
from app.schemas.ai import (
    AiInsightsRequest,
    AiQuestionRequest,
    AiQuestionResponse,
    AiStatusRead,
    AiVehicleInsights,
)
from app.services.ai_provider import (
    AiGenerationError,
    AiModelMissingError,
    AiProviderError,
    AiProviderUnavailableError,
)


router = APIRouter()


def _handle_ai_error(
    error:
        AiProviderError,
) -> None:
    if isinstance(
        error,
        (
            AiProviderUnavailableError,
            AiModelMissingError,
        ),
    ):
        raise HTTPException(
            status_code=(
                status
                .HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(
                error
            ),
        )

    if isinstance(
        error,
        AiGenerationError,
    ):
        raise HTTPException(
            status_code=(
                status
                .HTTP_502_BAD_GATEWAY
            ),
            detail=str(
                error
            ),
        )

    raise HTTPException(
        status_code=(
            status
            .HTTP_502_BAD_GATEWAY
        ),
        detail=(
            "The local AI service "
            "could not complete the "
            "request."
        ),
    )


@router.get(
    "/status",
    response_model=(
        AiStatusRead
    ),
)
def get_ai_status(
    ai_service:
        AiService,
) -> AiStatusRead:
    return (
        ai_service
        .status()
    )


@router.post(
    "/vehicle-insights",
    response_model=(
        AiVehicleInsights
    ),
)
def create_vehicle_insights(
    payload:
        AiInsightsRequest,
    ai_service:
        AiService,
) -> AiVehicleInsights:
    try:
        return (
            ai_service
            .generate_insights(
                payload.vehicle
            )
        )

    except AiProviderError as exc:
        _handle_ai_error(
            exc
        )

        raise


@router.post(
    "/vehicle-question",
    response_model=(
        AiQuestionResponse
    ),
)
def answer_vehicle_question(
    payload:
        AiQuestionRequest,
    ai_service:
        AiService,
) -> AiQuestionResponse:
    try:
        return (
            ai_service
            .answer_question(
                payload.vehicle,
                payload.question,
            )
        )

    except AiProviderError as exc:
        _handle_ai_error(
            exc
        )

        raise