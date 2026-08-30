from app.schemas.ai import (
    AiVehicleSnapshot,
)
from app.services.ai_vehicle_service import (
    VehicleAiService,
)


class FakeProvider:
    model = "qwen3:4b-instruct"

    def check_status(
        self,
    ):
        return (
            True,
            "Model ready.",
        )

    def generate_text(
        self,
        *,
        system_prompt,
        user_prompt,
        num_predict,
    ):
        return """
TONE: watch
SUMMARY: Recent MOTs show recurring tyre and suspension concerns.
INSIGHT_1_TITLE: Recurring tyre issues
INSIGHT_1_LEVEL: watch
INSIGHT_1_DETAIL: Tyre-related advisories appear across several recent MOTs.
INSIGHT_1_EVIDENCE: Tyre issues were recorded on multiple MOT tests.
INSIGHT_2_TITLE: Suspension items
INSIGHT_2_LEVEL: watch
INSIGHT_2_DETAIL: Suspension-related items also recur in the recent record.
INSIGHT_2_EVIDENCE: Suspension items occur on more than one MOT.
MILEAGE: Recorded mileage progresses consistently across the supplied tests.
SUPPLEMENTARY: NONE
"""


def test_ai_service_accepts_tagged_model_output():
    service = VehicleAiService(
        provider=(
            FakeProvider()
        )
    )

    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",
    )

    result = (
        service.generate_insights(
            vehicle
        )
    )

    assert (
        result.overall_tone
        == "watch"
    )

    assert (
        "Recent MOTs"
        in result.summary
    )

    assert (
        len(
            result.insights
        )
        >= 2
    )


def test_ai_service_fills_missing_fields_with_fallbacks():
    class PartialProvider(
        FakeProvider
    ):
        def generate_text(
            self,
            *,
            system_prompt,
            user_prompt,
            num_predict,
        ):
            return """
TONE: neutral
SUMMARY: The recent MOT record is mixed.
"""

    service = VehicleAiService(
        provider=(
            PartialProvider()
        )
    )

    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",
    )

    result = (
        service.generate_insights(
            vehicle
        )
    )

    assert (
        result.summary
        == (
            "The recent MOT "
            "record is mixed."
        )
    )

    assert (
        len(
            result.insights
        )
        >= 1
    )

    assert (
        result.mileage_analysis
    )