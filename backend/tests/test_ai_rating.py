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
                        449
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


def test_recent_unresolved_dangerous_defect_is_penalised_heavily():
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


def test_same_day_retest_does_not_double_count_advisories():
    advisory = (
        AiDefectInput(
            text=(
                "Rear brake disc worn, "
                "pitted or scored"
            ),

            type="ADVISORY",
        )
    )

    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        300
                    )
                ),

                test_result="PASSED",

                odometer_value=95000,

                defects=[
                    advisory,
                ],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        300
                    )
                ),

                test_result="FAILED",

                odometer_value=95000,

                defects=[
                    advisory,

                    AiDefectInput(
                        text=(
                            "Windscreen washer "
                            "provides insufficient "
                            "washer liquid"
                        ),

                        type="PRS",
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
        >= 95
    )


def test_old_dangerous_failure_resolved_immediately_is_discounted():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        1600
                    )
                ),

                test_result="PASSED",

                odometer_value=89000,

                defects=[],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        1600
                    )
                ),

                test_result="FAILED",

                odometer_value=89000,

                defects=[
                    AiDefectInput(
                        text=(
                            "Nearside front tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Offside front tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Nearside rear tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Offside rear tyre "
                            "tread depth below "
                            "requirements"
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
        >= 90
    )


def test_old_resolved_problems_do_not_overrule_clean_recent_history():
    shared_brake_advisories = [
        AiDefectInput(
            text=(
                "Rear brake disc worn, "
                "pitted or scored"
            ),

            type="ADVISORY",
        ),

        AiDefectInput(
            text=(
                "Front brake disc worn, "
                "but not excessively"
            ),

            type="ADVISORY",
        ),

        AiDefectInput(
            text=(
                "Front brake pads "
                "wearing thin"
            ),

            type="ADVISORY",
        ),
    ]

    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            # Latest MOT: completely clean.
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        180
                    )
                ),

                test_result="PASSED",

                odometer_value=98335,

                defects=[],
            ),

            # Pass after the 2025 retest.
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        550
                    )
                ),

                test_result="PASSED",

                odometer_value=95176,

                defects=(
                    shared_brake_advisories
                ),
            ),

            # Same-day failed test with the
            # same advisories plus a PRS item.
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        550
                    )
                ),

                test_result="FAILED",

                odometer_value=95176,

                defects=[
                    *shared_brake_advisories,

                    AiDefectInput(
                        text=(
                            "Front windscreen "
                            "washer provides "
                            "insufficient washer "
                            "liquid"
                        ),

                        type="PRS",
                    ),
                ],
            ),

            # Clean MOT.
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        900
                    )
                ),

                test_result="PASSED",

                odometer_value=93448,

                defects=[],
            ),

            # Older minor/advisory items.
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        1250
                    )
                ),

                test_result="PASSED",

                odometer_value=91692,

                defects=[
                    AiDefectInput(
                        text=(
                            "Nearside front tyre "
                            "obviously under "
                            "inflated"
                        ),

                        type="MINOR",
                    ),

                    AiDefectInput(
                        text=(
                            "Rear brake disc worn, "
                            "pitted or scored"
                        ),

                        type="ADVISORY",
                    ),
                ],
            ),

            # Old dangerous failure.
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        1650
                    )
                ),

                test_result="PASSED",

                odometer_value=89357,

                defects=[],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        1650
                    )
                ),

                test_result="FAILED",

                odometer_value=89349,

                defects=[
                    AiDefectInput(
                        text=(
                            "Nearside front tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Offside front tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Nearside rear tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Offside rear tyre "
                            "tread depth below "
                            "requirements"
                        ),

                        type="DANGEROUS",

                        dangerous=True,
                    ),

                    AiDefectInput(
                        text=(
                            "Front windscreen "
                            "washer provides "
                            "insufficient washer "
                            "liquid"
                        ),

                        type="MAJOR",
                    ),

                    AiDefectInput(
                        text=(
                            "Driver's view "
                            "significantly affected "
                            "by an obstruction"
                        ),

                        type="MAJOR",
                    ),

                    AiDefectInput(
                        text=(
                            "Rear brake pads "
                            "wearing thin"
                        ),

                        type="ADVISORY",
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
        75
        <= rating.score
        < 90
    )

    assert (
        rating.label
        == "Good"
    )


def test_many_current_advisories_still_reduce_rating():
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
                        20
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