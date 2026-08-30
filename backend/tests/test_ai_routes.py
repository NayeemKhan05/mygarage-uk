from app.api.dependencies.ai import (
    get_ai_service,
)
from app.main import app

from app.schemas.ai import (
    AiInsightItem,
    AiQuestionResponse,
    AiStatusRead,
    AiVehicleInsights,
)


class FakeAiService:
    def status(
        self,
    ):
        return AiStatusRead(
            available=True,
            model="qwen3:4b-instruct",
            message="Local model ready.",
        )

    def generate_insights(
        self,
        vehicle,
    ):
        return AiVehicleInsights(
            overall_tone="watch",

            summary=(
                "The supplied MOT history contains "
                "a recurring tyre pattern."
            ),

            rating={
                "score": 87,
                "label": "Good",
                "tone": "good",
                "explanation": (
                    "The recent MOT history is generally "
                    "positive, with only limited issues "
                    "affecting the rating."
                ),
            },

            mot_stats={
                "tests": 2,
                "passed": 2,
                "failed": 0,
                "recorded_items": 2,
                "dangerous": 0,
                "major": 0,
                "minor": 0,
                "advisory": 2,
                "prs": 0,
                "mileage_points": 2,
                "mileage_decreases": 0,
            },

            insights=[
                AiInsightItem(
                    title="Tyres recur",

                    detail=(
                        "Tyre-related items appear "
                        "across more than one MOT."
                    ),

                    level="watch",

                    evidence=(
                        "Tyre-related items appear "
                        "on two MOT tests."
                    ),
                ),
            ],

            recurring_items=[
                {
                    "label":
                        "Tyres and wheels",

                    "count":
                        2,

                    "latest_date":
                        "2026-01-01T00:00:00",
                },
            ],

            mileage_analysis=(
                "Recorded mileage increases consistently."
            ),

            supplementary_note=None,

            disclaimer="Test disclaimer",
        )

    def answer_question(
        self,
        vehicle,
        question,
    ):
        return AiQuestionResponse(
            answer=(
                "The supplied MOT record contains "
                "repeated tyre-related items."
            ),

            disclaimer="Test disclaimer",
        )


def vehicle_payload():
    return {
        "registration":
            "AB12CDE",

        "make":
            "Honda",

        "model":
            "Civic",

        "year":
            2012,

        "fuel_type":
            "Petrol",

        "mot_tests": [
            {
                "completed_at":
                    "2026-01-01T10:00:00",

                "test_result":
                    "PASSED",

                "odometer_value":
                    80000,

                "odometer_unit":
                    "mi",

                "defects": [],
            },
        ],
    }


def test_ai_status(
    client,
):
    app.dependency_overrides[
        get_ai_service
    ] = (
        lambda:
            FakeAiService()
    )

    try:
        response = client.get(
            "/api/v1/ai/status"
        )

        assert (
            response.status_code
            == 200
        )

        assert (
            response
            .json()[
                "available"
            ]
            is True
        )

    finally:
        app.dependency_overrides.pop(
            get_ai_service,
            None,
        )


def test_vehicle_insights(
    client,
):
    app.dependency_overrides[
        get_ai_service
    ] = (
        lambda:
            FakeAiService()
    )

    try:
        response = client.post(
            "/api/v1/ai/vehicle-insights",

            json={
                "vehicle":
                    vehicle_payload(),
            },
        )

        assert (
            response.status_code
            == 200
        )

        body = response.json()

        assert (
            body[
                "overall_tone"
            ]
            == "watch"
        )

        assert (
            body[
                "rating"
            ][
                "score"
            ]
            == 87
        )

        assert (
            body[
                "rating"
            ][
                "label"
            ]
            == "Good"
        )

    finally:
        app.dependency_overrides.pop(
            get_ai_service,
            None,
        )


def test_vehicle_question(
    client,
):
    app.dependency_overrides[
        get_ai_service
    ] = (
        lambda:
            FakeAiService()
    )

    try:
        response = client.post(
            "/api/v1/ai/vehicle-question",

            json={
                "vehicle":
                    vehicle_payload(),

                "question":
                    (
                        "What keeps "
                        "appearing?"
                    ),
            },
        )

        assert (
            response.status_code
            == 200
        )

        assert (
            "tyre"
            in response
            .json()[
                "answer"
            ]
            .lower()
        )

    finally:
        app.dependency_overrides.pop(
            get_ai_service,
            None,
        )