from datetime import datetime, timedelta

from app.schemas.ai import (
    AiDefectInput,
    AiMotTestInput,
    AiVehicleSnapshot,
)
from app.services.ai_context import (
    build_vehicle_context,
)
from app.services.ai_rating import (
    _rating_band,
    build_vehicle_rating,
)


def recent_date(
    days_ago: int,
) -> datetime:
    return (
        datetime.now()
        - timedelta(
            days=days_ago
        )
    )


def test_rating_bands_are_user_friendly():
    assert (
        _rating_band(
            100
        )[0]
        == "Excellent"
    )

    assert (
        _rating_band(
            90
        )[0]
        == "Excellent"
    )

    assert (
        _rating_band(
            89
        )[0]
        == "Good"
    )

    assert (
        _rating_band(
            84
        )[0]
        == "Good"
    )

    assert (
        _rating_band(
            75
        )[0]
        == "Good"
    )

    assert (
        _rating_band(
            74
        )[0]
        == "Fair"
    )

    assert (
        _rating_band(
            60
        )[0]
        == "Fair"
    )

    assert (
        _rating_band(
            59
        )[0]
        == "Needs attention"
    )

    assert (
        _rating_band(
            40
        )[0]
        == "Needs attention"
    )

    assert (
        _rating_band(
            39
        )[0]
        == "Concerning"
    )


def test_minor_failure_does_not_destroy_rating():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        100
                    )
                ),

                test_result="PASSED",

                defects=[],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        450
                    )
                ),

                test_result="FAILED",

                defects=[
                    AiDefectInput(
                        text=(
                            "Rear position "
                            "lamp not working"
                        ),

                        type="MINOR",
                    ),
                ],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        800
                    )
                ),

                test_result="PASSED",

                defects=[],
            ),
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    rating = (
        build_vehicle_rating(
            context
        )
    )

    assert (
        rating.score
        >= 90
    )

    assert (
        rating.label
        == "Excellent"
    )


def test_many_recent_advisories_reduce_rating():
    advisories = [
        AiDefectInput(
            text=(
                f"Advisory item "
                f"{index}"
            ),

            type="ADVISORY",
        )
        for index in range(
            15
        )
    ]

    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        30
                    )
                ),

                test_result="PASSED",

                defects=advisories,
            ),
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    rating = (
        build_vehicle_rating(
            context
        )
    )

    assert (
        rating.score
        < 90
    )

    assert (
        rating.label
        in {
            "Good",
            "Fair",
            "Needs attention",
            "Concerning",
        }
    )


def test_dangerous_defects_have_large_effect():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        20
                    )
                ),

                test_result="FAILED",

                defects=[
                    AiDefectInput(
                        text=(
                            "Dangerous brake "
                            "defect"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),
                ],
            ),
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    rating = (
        build_vehicle_rating(
            context
        )
    )

    assert (
        rating.score
        < 75
    )

    assert (
        rating.label
        in {
            "Fair",
            "Needs attention",
            "Concerning",
        }
    )


def test_clean_recent_history_rates_highly():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        30
                    )
                ),

                test_result="PASSED",

                defects=[],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        400
                    )
                ),

                test_result="PASSED",

                defects=[],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        800
                    )
                ),

                test_result="PASSED",

                defects=[],
            ),
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    rating = (
        build_vehicle_rating(
            context
        )
    )

    assert (
        rating.score
        >= 90
    )

    assert (
        rating.label
        == "Excellent"
    )