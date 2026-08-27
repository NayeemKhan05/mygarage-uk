from datetime import (
    datetime,
)

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


def test_recurring_components_are_counted_by_mot():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",
        make="Honda",
        model="Civic",
        mot_tests=[
            AiMotTestInput(
                completed_at=datetime(
                    2026,
                    1,
                    1,
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
                completed_at=datetime(
                    2025,
                    1,
                    1,
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
                completed_at=datetime(
                    2026,
                    1,
                    1,
                ),
                test_result="FAILED",
                defects=[
                    AiDefectInput(
                        text=(
                            "Brake defect"
                        ),
                        type="MAJOR",
                    ),
                    AiDefectInput(
                        text=(
                            "Tyre advisory"
                        ),
                        type="ADVISORY",
                    ),
                ],
            ),
            AiMotTestInput(
                completed_at=datetime(
                    2025,
                    1,
                    1,
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


def test_missing_manual_history_is_not_added_to_context():
    vehicle = AiVehicleSnapshot(
        registration="AB12CDE",
        mot_tests=[],
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


def test_manual_history_is_clearly_supplementary():
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

    supplementary = (
        context[
            "supplementary_user_records"
        ]
    )

    assert (
        "partial"
        in supplementary[
            "warning"
        ].lower()
    )