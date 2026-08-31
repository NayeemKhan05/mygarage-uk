import re

from datetime import date, datetime
from typing import Any

from app.schemas.ai import (
    AiVehicleRating,
)


SEVERITY_PENALTIES = {
    "DANGEROUS": 18.0,
    "MAJOR": 8.0,
    "ADVISORY": 1.5,
    "MINOR": 0.6,
    "PRS": 0.2,
}


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


def _normalise_issue_text(
    value: str,
) -> str:
    cleaned = (
        value
        .lower()
        .strip()
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    )

    return cleaned


def _age_weight(
    test_date: date | None,
    analysis_date: date,
) -> float:
    if test_date is None:
        return 0.5

    days_old = (
        analysis_date
        - test_date
    ).days

    if days_old <= 365:
        return 1.0

    if days_old <= 730:
        return 0.85

    if days_old <= 1095:
        return 0.65

    if days_old <= 1460:
        return 0.45

    return 0.25


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


def _test_mileage(
    test: dict[str, Any],
) -> int | None:
    value = (
        test.get(
            "mileage"
        )
    )

    if isinstance(
        value,
        int,
    ):
        return value

    return None


def _mileages_are_close(
    first: int | None,
    second: int | None,
) -> bool:
    if (
        first is None
        or second is None
    ):
        return True

    return (
        abs(
            first
            - second
        )
        <= 250
    )


def _find_resolving_pass(
    history: list[
        dict[str, Any]
    ],
    failed_index: int,
) -> int | None:
    failed_test = (
        history[
            failed_index
        ]
    )

    failed_date = (
        _parse_date(
            failed_test.get(
                "date"
            )
        )
    )

    if failed_date is None:
        return None

    failed_mileage = (
        _test_mileage(
            failed_test
        )
    )

    # History is stored newest first.
    # Walk towards the newer tests, beginning
    # with the test immediately after the failure.
    for index in range(
        failed_index - 1,
        -1,
        -1,
    ):
        newer_test = (
            history[
                index
            ]
        )

        result = (
            str(
                newer_test.get(
                    "result",
                    "UNKNOWN",
                )
            )
            .upper()
        )

        if result != "PASSED":
            continue

        newer_date = (
            _parse_date(
                newer_test.get(
                    "date"
                )
            )
        )

        if newer_date is None:
            continue

        days_between = (
            newer_date
            - failed_date
        ).days

        if days_between < 0:
            continue

        if days_between > 30:
            break

        newer_mileage = (
            _test_mileage(
                newer_test
            )
        )

        if not _mileages_are_close(
            failed_mileage,
            newer_mileage,
        ):
            continue

        return days_between

    return None


def _resolution_multiplier(
    days_to_pass: int | None,
) -> float:
    if days_to_pass is None:
        return 1.0

    if days_to_pass <= 2:
        return 0.20

    if days_to_pass <= 14:
        return 0.30

    if days_to_pass <= 30:
        return 0.40

    return 1.0


def _is_duplicate_issue(
    *,
    text: str,
    test_date: date | None,
    mileage: int | None,
    seen: dict[
        str,
        list[
            tuple[
                date | None,
                int | None,
            ]
        ],
    ],
) -> bool:
    normalised = (
        _normalise_issue_text(
            text
        )
    )

    previous_occurrences = (
        seen.get(
            normalised,
            [],
        )
    )

    for (
        previous_date,
        previous_mileage,
    ) in previous_occurrences:
        if (
            test_date is not None
            and previous_date
            is not None
        ):
            days_between = abs(
                (
                    previous_date
                    - test_date
                ).days
            )

            if days_between > 30:
                continue

        if not _mileages_are_close(
            mileage,
            previous_mileage,
        ):
            continue

        return True

    seen.setdefault(
        normalised,
        [],
    ).append(
        (
            test_date,
            mileage,
        )
    )

    return False


def _recurring_penalty(
    recurring_components: list[
        dict[str, Any]
    ],
    analysis_date: date,
) -> float:
    penalty = 0.0

    for item in recurring_components:
        count = int(
            item.get(
                "test_count",
                0,
            )
        )

        if count < 2:
            continue

        if count >= 4:
            base_penalty = 3.5

        elif count == 3:
            base_penalty = 2.0

        else:
            base_penalty = 1.0

        latest_date = (
            _parse_date(
                item.get(
                    "latest_date"
                )
            )
        )

        recency = (
            _age_weight(
                latest_date,
                analysis_date,
            )
        )

        penalty += (
            base_penalty
            * recency
        )

    return min(
        penalty,
        7.0,
    )


def _latest_test_bonus(
    history: list[
        dict[str, Any]
    ],
) -> float:
    if not history:
        return 0.0

    latest = history[0]

    result = (
        str(
            latest.get(
                "result",
                "UNKNOWN",
            )
        )
        .upper()
    )

    if result != "PASSED":
        return 0.0

    items = (
        latest.get(
            "recorded_items",
            [],
        )
    )

    if not items:
        return 2.0

    serious_items = [
        item
        for item in items
        if (
            str(
                item.get(
                    "type",
                    "",
                )
            )
            .upper()
            in {
                "MAJOR",
                "DANGEROUS",
            }
        )
    ]

    if serious_items:
        return 0.0

    if len(items) <= 2:
        return 0.75

    return 0.0


def _build_explanation(
    *,
    score: int,
    statistics: dict[str, Any],
    latest_clean: bool,
    resolved_serious_count: int,
    unresolved_dangerous_count: int,
    unresolved_major_count: int,
    recurring_components: list[
        dict[str, Any]
    ],
) -> str:
    if score >= 90:
        base = (
            "The recent MOT history is very positive, "
            "with relatively few current concerns."
        )

    elif score >= 75:
        base = (
            "The recent MOT history is generally positive, "
            "although some recorded issues are worth reviewing."
        )

    elif score >= 60:
        base = (
            "The recent MOT history is mixed, with several "
            "issues worth reviewing more closely."
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
            "or unresolved serious concerns that should "
            "be reviewed carefully."
        )

    details: list[str] = []

    if latest_clean:
        details.append(
            (
                "The latest MOT passed with no recorded "
                "defects or advisories, which carries "
                "significant weight in the rating."
            )
        )

    if unresolved_dangerous_count > 0:
        details.append(
            (
                f"The recent record includes "
                f"{unresolved_dangerous_count} dangerous "
                f"{'defect' if unresolved_dangerous_count == 1 else 'defects'} "
                "without a prompt passing retest."
            )
        )

    elif unresolved_major_count > 0:
        details.append(
            (
                f"The recent record includes "
                f"{unresolved_major_count} major "
                f"{'defect' if unresolved_major_count == 1 else 'defects'} "
                "without a prompt passing retest."
            )
        )

    elif resolved_serious_count > 0:
        details.append(
            (
                "Older serious defects that were followed "
                "by a prompt passing retest have a much "
                "smaller effect than unresolved recent defects."
            )
        )

    elif (
        statistics[
            "advisory"
        ]
        >= 10
    ):
        details.append(
            (
                "A relatively high number of advisories "
                "has been recorded across the analysis period."
            )
        )

    elif len(
        recurring_components
    ) >= 2:
        details.append(
            (
                "Some component areas have appeared "
                "on more than one recent MOT."
            )
        )

    return " ".join(
        [
            base,
            *details[:2],
        ]
    )


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

    seen_issues: dict[
        str,
        list[
            tuple[
                date | None,
                int | None,
            ]
        ],
    ] = {}

    resolved_serious_count = 0
    unresolved_dangerous_count = 0
    unresolved_major_count = 0

    for index, test in enumerate(
        history
    ):
        test_date = (
            _parse_date(
                test.get(
                    "date"
                )
            )
        )

        mileage = (
            _test_mileage(
                test
            )
        )

        age_weight = (
            _age_weight(
                test_date,
                analysis_date,
            )
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

        days_to_pass = None

        if result == "FAILED":
            days_to_pass = (
                _find_resolving_pass(
                    history,
                    index,
                )
            )

            if days_to_pass is None:
                score -= (
                    1.5
                    * age_weight
                )

            else:
                score -= (
                    0.4
                    * age_weight
                )

        resolution_multiplier = (
            _resolution_multiplier(
                days_to_pass
            )
        )

        items = (
            test.get(
                "recorded_items",
                [],
            )
        )

        dangerous_on_test = 0
        major_on_test = 0

        for item in items:
            item_type = (
                str(
                    item.get(
                        "type",
                        "UNKNOWN",
                    )
                )
                .upper()
            )

            item_text = (
                str(
                    item.get(
                        "text",
                        "",
                    )
                )
            )

            if not item_text:
                continue

            # A failed MOT and its immediate retest
            # often repeat the same advisory wording.
            # Count that issue once rather than twice.
            if _is_duplicate_issue(
                text=item_text,
                test_date=test_date,
                mileage=mileage,
                seen=seen_issues,
            ):
                continue

            base_penalty = (
                SEVERITY_PENALTIES.get(
                    item_type,
                    0.5,
                )
            )

            effective_penalty = (
                base_penalty
                * age_weight
            )

            if (
                result == "FAILED"
                and days_to_pass
                is not None
            ):
                effective_penalty *= (
                    resolution_multiplier
                )

                if item_type in {
                    "DANGEROUS",
                    "MAJOR",
                }:
                    resolved_serious_count += 1

            elif (
                result == "FAILED"
                and days_to_pass
                is None
            ):
                if (
                    item_type
                    == "DANGEROUS"
                ):
                    unresolved_dangerous_count += 1
                    dangerous_on_test += 1

                elif (
                    item_type
                    == "MAJOR"
                ):
                    unresolved_major_count += 1
                    major_on_test += 1

            score -= (
                effective_penalty
            )

        # An unresolved serious failed MOT deserves
        # an additional penalty because there is no
        # nearby passing retest showing correction.
        if (
            result == "FAILED"
            and days_to_pass
            is None
        ):
            unresolved_penalty = (
                dangerous_on_test
                * 8.0
                + major_on_test
                * 3.0
            )

            score -= (
                min(
                    unresolved_penalty,
                    30.0,
                )
                * age_weight
            )

    score -= (
        _recurring_penalty(
            recurring_components,
            analysis_date,
        )
    )

    mileage_decreases = int(
        statistics[
            "mileage_decreases"
        ]
    )

    score -= min(
        mileage_decreases
        * 3.0,
        6.0,
    )

    score += (
        _latest_test_bonus(
            history
        )
    )

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

    latest_clean = False

    if history:
        latest = history[0]

        latest_clean = (
            str(
                latest.get(
                    "result",
                    "",
                )
            ).upper()
            == "PASSED"
            and not latest.get(
                "recorded_items",
                [],
            )
        )

    explanation = (
        _build_explanation(
            score=final_score,
            statistics=statistics,
            latest_clean=latest_clean,
            resolved_serious_count=(
                resolved_serious_count
            ),
            unresolved_dangerous_count=(
                unresolved_dangerous_count
            ),
            unresolved_major_count=(
                unresolved_major_count
            ),
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