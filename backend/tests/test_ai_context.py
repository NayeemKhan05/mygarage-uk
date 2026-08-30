from datetime import datetime, timedelta

from app.schemas.ai import (
    AiDefectInput,
    AiMotTestInput,
    AiVehicleSnapshot,
)
from app.services.ai_context import (
    build_mot_stats,
    build_recurring_items,
    build_vehicle_context,
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


def test_recurring_components_are_counted_by_mot():
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

                defects=[
                    AiDefectInput(
                        text=(
                            "Nearside front "
                            "tyre worn close "
                            "to legal limit"
                        ),

                        type="ADVISORY",
                    ),
                ],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        400
                    )
                ),

                test_result="PASSED",

                defects=[
                    AiDefectInput(
                        text=(
                            "Offside rear "
                            "tyre worn"
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

    recurring = (
        build_recurring_items(
            context
        )
    )

    assert len(
        recurring
    ) == 1

    assert (
        recurring[0].label
        == "Tyres and wheels"
    )

    assert (
        recurring[0].count
        == 2
    )


def test_mot_statistics_are_deterministic():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        100
                    )
                ),

                test_result="FAILED",

                defects=[
                    AiDefectInput(
                        text="Brake defect",
                        type="MAJOR",
                    ),

                    AiDefectInput(
                        text="Tyre advisory",
                        type="ADVISORY",
                    ),
                ],
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
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    stats = (
        build_mot_stats(
            context
        )
    )

    assert stats.tests == 2
    assert stats.passed == 1
    assert stats.failed == 1

    assert (
        stats.recorded_items
        == 2
    )

    assert stats.major == 1
    assert stats.advisory == 1


def test_missing_manual_history_is_not_added():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    assert (
        "supplementary_user_records"
        not in context
    )


def test_manual_history_is_supplementary():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        supplementary_service_records=[
            {
                "category":
                    "service",

                "notes":
                    (
                        "Oil and filter "
                        "changed"
                    ),
            },
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    warning = (
        context[
            "supplementary_user_records"
        ][
            "warning"
        ].lower()
    )

    assert (
        "partial"
        in warning
    )

    assert (
        "supplementary"
        in warning
    )


def test_every_mot_item_is_preserved():
    defects = [
        AiDefectInput(
            text=(
                f"Advisory number "
                f"{index}"
            ),

            type="ADVISORY",
        )
        for index
        in range(
            1,
            11,
        )
    ]

    defects[-1] = (
        AiDefectInput(
            text="Coolant leak",
            type="ADVISORY",
        )
    )

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

                defects=defects,
            ),
        ],
    )

    context = (
        build_vehicle_context(
            vehicle
        )
    )

    history = (
        context[
            "mot_analysis"
        ][
            "mot_history"
        ]
    )

    latest = history[0]

    assert (
        latest[
            "recorded_item_count"
        ]
        == 10
    )

    assert len(
        latest[
            "recorded_items"
        ]
    ) == 10

    assert any(
        item["text"]
        == "Coolant leak"
        for item
        in latest[
            "recorded_items"
        ]
    )


def test_all_mots_within_five_years_are_preserved():
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

                defects=[
                    AiDefectInput(
                        text="Coolant leak",
                        type="ADVISORY",
                    ),
                ],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        500
                    )
                ),

                test_result="FAILED",

                defects=[
                    AiDefectInput(
                        text="Brake defect",
                        type="MAJOR",
                    ),
                ],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        900
                    )
                ),

                test_result="PASSED",

                defects=[
                    AiDefectInput(
                        text="Tyre advisory",
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

    history = (
        context[
            "mot_analysis"
        ][
            "mot_history"
        ]
    )

    assert len(
        history
    ) == 3

    assert (
        history[0][
            "recorded_items"
        ][0]["text"]
        == "Coolant leak"
    )

    assert (
        history[1][
            "recorded_items"
        ][0]["text"]
        == "Brake defect"
    )

    assert (
        history[2][
            "recorded_items"
        ][0]["text"]
        == "Tyre advisory"
    )


def test_mots_older_than_five_years_are_excluded():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",

        mot_tests=[
            AiMotTestInput(
                completed_at=(
                    recent_date(
                        365
                    )
                ),

                test_result="PASSED",

                defects=[
                    AiDefectInput(
                        text=(
                            "Recent tyre "
                            "advisory"
                        ),

                        type="ADVISORY",
                    ),
                ],
            ),

            AiMotTestInput(
                completed_at=(
                    recent_date(
                        365 * 7
                    )
                ),

                test_result="FAILED",

                defects=[
                    AiDefectInput(
                        text=(
                            "Old brake "
                            "failure"
                        ),

                        type="MAJOR",
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

    stats = (
        build_mot_stats(
            context
        )
    )

    assert stats.tests == 1
    assert stats.passed == 1
    assert stats.failed == 0

    assert (
        context[
            "analysis_scope"
        ][
            "total_mot_tests_available"
        ]
        == 2
    )

    assert (
        context[
            "analysis_scope"
        ][
            "mot_tests_analysed"
        ]
        == 1
    )