from datetime import date, datetime
from typing import Any

from app.schemas.ai import (
    AiVehicleRating,
)


def _parse_date(
    value: str | None,
) -> date | None:
    if not value:
        return None

    try:
        return (
            datetime
            .fromisoformat(
                value
            )
            .date()
        )

    except ValueError:
        return None


def _age_weight(
    test_date: date | None,
    analysis_date: date,
) -> float:
    if test_date is None:
        return 0.6

    days_old = (
        analysis_date
        - test_date
    ).days

    if days_old <= 365:
        return 1.0

    if days_old <= 730:
        return 0.85

    if days_old <= 1095:
        return 0.70

    if days_old <= 1460:
        return 0.55

    return 0.40


def _rating_band(
    score: int,
) -> tuple[str, str]:
    if score >= 90:
        return (
            "Excellent",
            "excellent",
        )

    if score >= 75:
        return (
            "Good",
            "good",
        )

    if score >= 60:
        return (
            "Fair",
            "fair",
        )

    if score >= 40:
        return (
            "Needs attention",
            "attention",
        )

    return (
        "Concerning",
        "concerning",
    )


def _build_explanation(
    *,
    score: int,
    statistics: dict[str, Any],
    recurring_components: list[
        dict[str, Any]
    ],
) -> str:
    dangerous = (
        statistics[
            "dangerous"
        ]
    )

    major = (
        statistics[
            "major"
        ]
    )

    advisory = (
        statistics[
            "advisory"
        ]
    )

    failed = (
        statistics[
            "failed"
        ]
    )

    if score >= 90:
        base = (
            "The recent MOT history is very positive, "
            "with few significant recorded concerns."
        )

    elif score >= 75:
        base = (
            "The recent MOT history is generally positive, "
            "although some recorded issues are worth reviewing."
        )

    elif score >= 60:
        base = (
            "The recent MOT history is mixed, with several "
            "recorded issues worth reviewing more closely."
        )

    elif score >= 40:
        base = (
            "The recent MOT history contains a number of "
            "significant or repeated issues that deserve "
            "closer attention."
        )

    else:
        base = (
            "The recent MOT history contains substantial "
            "or repeated serious concerns that should be "
            "reviewed carefully."
        )

    if dangerous > 0:
        return (
            f"{base} The record includes "
            f"{dangerous} dangerous "
            f"{'defect' if dangerous == 1 else 'defects'}, "
            "which has a significant effect on the rating."
        )

    if major >= 2:
        return (
            f"{base} The record includes "
            f"{major} major defects during the "
            "analysis period."
        )

    if advisory >= 10:
        return (
            f"{base} A relatively high number of "
            "advisories has also been recorded "
            "across recent MOTs."
        )

    if len(
        recurring_components
    ) >= 2:
        return (
            f"{base} Several component areas have "
            "appeared on more than one recent MOT."
        )

    if failed > 0:
        return (
            f"{base} Failed MOTs are considered, "
            "but a failure on its own has much less "
            "impact than major or dangerous defects."
        )

    return base


def build_vehicle_rating(
    context: dict[str, Any],
) -> AiVehicleRating:
    analysis = (
        context[
            "mot_analysis"
        ]
    )

    history = (
        analysis[
            "mot_history"
        ]
    )

    statistics = (
        analysis[
            "statistics"
        ]
    )

    recurring_components = (
        analysis[
            "recurring_components"
        ]
    )

    analysis_date = (
        date.fromisoformat(
            context[
                "analysis_date"
            ]
        )
    )

    score = 100.0

    for test in history:
        test_date = (
            _parse_date(
                test.get(
                    "date"
                )
            )
        )

        weight = (
            _age_weight(
                test_date,
                analysis_date,
            )
        )

        items = (
            test.get(
                "recorded_items",
                [],
            )
        )

        item_types = [
            str(
                item.get(
                    "type",
                    "UNKNOWN",
                )
            ).upper()
            for item in items
        ]

        has_serious_defect = any(
            item_type
            in {
                "MAJOR",
                "DANGEROUS",
            }
            for item_type
            in item_types
        )

        result = (
            str(
                test.get(
                    "result",
                    "UNKNOWN",
                )
            )
            .upper()
        )

        # A failed MOT itself is only a small penalty.
        # The recorded defect severity matters much more.
        if result == "FAILED":
            if has_serious_defect:
                score -= (
                    4.0
                    * weight
                )

            else:
                score -= (
                    1.5
                    * weight
                )

        for item_type in item_types:
            if item_type == "DANGEROUS":
                score -= (
                    25.0
                    * weight
                )

            elif item_type == "MAJOR":
                score -= (
                    7.0
                    * weight
                )

            elif item_type == "ADVISORY":
                score -= (
                    1.3
                    * weight
                )

            elif item_type == "MINOR":
                score -= (
                    0.5
                    * weight
                )

            elif item_type == "PRS":
                score -= (
                    0.25
                    * weight
                )

    # Repeated component areas matter, but should not
    # overwhelm the actual severity of the MOT defects.
    recurring_penalty = 0.0

    for item in recurring_components:
        count = int(
            item.get(
                "test_count",
                0,
            )
        )

        if count >= 4:
            recurring_penalty += 3.0

        elif count == 3:
            recurring_penalty += 2.0

        elif count == 2:
            recurring_penalty += 1.0

    score -= min(
        recurring_penalty,
        8.0,
    )

    # Mileage decreases are worth flagging, but do not
    # automatically imply anything improper.
    mileage_decreases = int(
        statistics[
            "mileage_decreases"
        ]
    )

    score -= min(
        mileage_decreases
        * 4.0,
        8.0,
    )

    # A completely clean latest MOT is mildly positive.
    if history:
        latest = history[0]

        latest_result = (
            str(
                latest.get(
                    "result",
                    "UNKNOWN",
                )
            )
            .upper()
        )

        latest_items = (
            latest.get(
                "recorded_items",
                [],
            )
        )

        if (
            latest_result == "PASSED"
            and len(
                latest_items
            ) == 0
        ):
            score += 2.0

    final_score = round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        )
    )

    label, tone = (
        _rating_band(
            final_score
        )
    )

    explanation = (
        _build_explanation(
            score=final_score,
            statistics=statistics,
            recurring_components=(
                recurring_components
            ),
        )
    )

    return AiVehicleRating(
        score=final_score,
        label=label,
        tone=tone,
        explanation=explanation,
    )