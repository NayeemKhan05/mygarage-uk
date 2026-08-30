import json

from typing import Any

from app.schemas.ai import (
    AiGeneratedNarrative,
    AiInsightItem,
    AiQuestionResponse,
    AiStatusRead,
    AiVehicleInsights,
    AiVehicleSnapshot,
)
from app.services.ai_context import (
    AI_HISTORY_YEARS,
    build_mot_stats,
    build_recurring_items,
    build_vehicle_context,
)
from app.services.ai_provider import (
    AiProvider,
)


INSIGHT_SYSTEM_PROMPT = """
You are the AI Vehicle Insights feature for MyGarage UK.

Analyse UK vehicle MOT history carefully.

DVSA MOT history is the primary evidence.

The supplied vehicle data contains every MOT and every recorded MOT item
from the most recent analysis window.

Backend-calculated statistics and recurring component counts are
authoritative.

User-entered service and maintenance records, if supplied, are
supplementary only and may be incomplete.

RULES

- Examine every recorded item in the supplied MOT history.
- Do not stop after the first few advisories.
- Never invent defects, dates, mileage, repairs or counts.
- Never contradict the supplied backend statistics.
- Focus on meaningful patterns across MOTs.
- Pay particular attention to recurring component areas.
- Consider failures, major defects, dangerous defects and advisories.
- A passed MOT does not prove perfect mechanical condition.
- Never infer poor maintenance because user-entered service records are
  missing.
- Do not diagnose faults.
- Do not predict future failures.
- A mileage decrease is an inconsistency, not proof of clocking.
- Do not give a simplistic buy or don't-buy verdict.
- Use British English.

Your output MUST use the following labels.

Keep every value on one concise line.

TONE: positive, neutral, watch or attention
SUMMARY: overall MOT-history summary

INSIGHT_1_TITLE:
INSIGHT_1_LEVEL: positive, info, watch or attention
INSIGHT_1_DETAIL:
INSIGHT_1_EVIDENCE:

INSIGHT_2_TITLE:
INSIGHT_2_LEVEL: positive, info, watch or attention
INSIGHT_2_DETAIL:
INSIGHT_2_EVIDENCE:

INSIGHT_3_TITLE:
INSIGHT_3_LEVEL: positive, info, watch or attention
INSIGHT_3_DETAIL:
INSIGHT_3_EVIDENCE:

MILEAGE: concise mileage analysis

SUPPLEMENTARY: useful supplementary user-record context, or NONE

Do not add any other sections.
Do not use Markdown.
"""


QUESTION_SYSTEM_PROMPT = """
You answer questions about one vehicle in MyGarage UK.

Use only the supplied vehicle evidence.

The MOT history supplied contains every recorded item from every MOT in
the recent analysis window.

DVSA MOT data is the primary evidence.

Backend-calculated statistics are authoritative.

User-entered service and maintenance records may be incomplete and are
supplementary only.

RULES

- Read every relevant recorded MOT item.
- Do not stop at the first few advisories.
- Never invent defects, repairs, dates, mileage, services or MOT results.
- Never infer poor maintenance because user-entered history is absent.
- Do not diagnose mechanical faults.
- Do not guarantee future reliability.
- Do not claim clocking from a mileage decrease alone.
- Do not give unsupported buying verdicts.
- If the records cannot answer the question, say so clearly.
- Use British English.
- Answer the question directly.
- Keep the response useful but concise.

Return plain text only.
"""


DISCLAIMER = (
    "AI-generated interpretation of the supplied "
    "vehicle records. It is not a mechanical "
    "inspection, diagnosis or guarantee of "
    "vehicle condition."
)


VALID_TONES = {
    "positive",
    "neutral",
    "watch",
    "attention",
}


VALID_LEVELS = {
    "positive",
    "info",
    "watch",
    "attention",
}


OUTPUT_FIELDS = (
    "TONE",
    "SUMMARY",
    "INSIGHT_1_TITLE",
    "INSIGHT_1_LEVEL",
    "INSIGHT_1_DETAIL",
    "INSIGHT_1_EVIDENCE",
    "INSIGHT_2_TITLE",
    "INSIGHT_2_LEVEL",
    "INSIGHT_2_DETAIL",
    "INSIGHT_2_EVIDENCE",
    "INSIGHT_3_TITLE",
    "INSIGHT_3_LEVEL",
    "INSIGHT_3_DETAIL",
    "INSIGHT_3_EVIDENCE",
    "MILEAGE",
    "SUPPLEMENTARY",
)


def _compact_json(
    value: dict[str, Any],
) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )


def _parse_tagged_output(
    text: str,
) -> dict[str, str]:
    values: dict[str, str] = {}

    current_field: str | None = None

    for raw_line in text.splitlines():
        line = (
            raw_line
            .strip()
            .lstrip("-* ")
            .strip()
        )

        if not line:
            continue

        if line.startswith("```"):
            continue

        upper_line = (
            line.upper()
        )

        matched = False

        for field in OUTPUT_FIELDS:
            prefix = (
                f"{field}:"
            )

            if upper_line.startswith(
                prefix
            ):
                value = (
                    line[
                        len(prefix):
                    ]
                    .strip()
                )

                values[field] = value
                current_field = field
                matched = True

                break

        if (
            not matched
            and current_field
        ):
            previous = (
                values.get(
                    current_field,
                    "",
                )
            )

            values[
                current_field
            ] = (
                f"{previous} {line}"
                .strip()
            )

    return values


def _fallback_tone(
    context: dict[str, Any],
) -> str:
    stats = (
        context[
            "mot_analysis"
        ][
            "statistics"
        ]
    )

    recurring = (
        context[
            "mot_analysis"
        ][
            "recurring_components"
        ]
    )

    if (
        stats["dangerous"] > 0
        or stats["major"] >= 2
        or stats["failed"] >= 2
    ):
        return "attention"

    if (
        stats["failed"] > 0
        or stats["major"] > 0
        or recurring
    ):
        return "watch"

    if (
        stats["recorded_items"] == 0
        and stats["failed"] == 0
    ):
        return "positive"

    return "neutral"


def _fallback_summary(
    context: dict[str, Any],
) -> str:
    stats = (
        context[
            "mot_analysis"
        ][
            "statistics"
        ]
    )

    recurring = (
        context[
            "mot_analysis"
        ][
            "recurring_components"
        ]
    )

    summary = (
        f"The recent MOT record contains "
        f"{stats['tests']} tests, with "
        f"{stats['passed']} passes and "
        f"{stats['failed']} failures. "
        f"There are "
        f"{stats['recorded_items']} recorded "
        f"MOT items in the analysis window."
    )

    if recurring:
        labels = ", ".join(
            item["label"]
            for item
            in recurring[:3]
        )

        summary += (
            " Recurring recorded areas "
            f"include {labels}."
        )

    return summary


def _fallback_mileage(
    context: dict[str, Any],
) -> str:
    mileage = (
        context[
            "mot_analysis"
        ][
            "mileage"
        ]
    )

    points = (
        mileage[
            "points"
        ]
    )

    if not points:
        return (
            "There are not enough recorded "
            "mileage readings in the analysis "
            "window to describe a trend."
        )

    first = points[0]
    latest = points[-1]

    if (
        mileage[
            "recorded_decreases"
        ] > 0
    ):
        return (
            "The recorded mileage generally "
            "progresses through the MOT history, "
            "but at least one decrease appears "
            "in the supplied readings and would "
            "need checking against the original "
            "records."
        )

    annual = (
        mileage[
            "annual_distance_estimate"
        ]
    )

    if annual:
        return (
            f"Recorded mileage rises from "
            f"{first['value']:,} to "
            f"{latest['value']:,} "
            f"{latest['unit'] or ''} across the "
            f"analysis period, equivalent to "
            f"roughly {annual['estimate']:,} "
            f"{annual['unit'] or ''} per year "
            f"between the first and latest "
            f"recorded readings."
        )

    return (
        f"Recorded mileage rises from "
        f"{first['value']:,} to "
        f"{latest['value']:,} "
        f"{latest['unit'] or ''} across the "
        f"available recent MOT readings."
    )


def _fallback_insights(
    context: dict[str, Any],
) -> list[AiInsightItem]:
    result: list[AiInsightItem] = []

    analysis = (
        context[
            "mot_analysis"
        ]
    )

    stats = (
        analysis[
            "statistics"
        ]
    )

    recurring = (
        analysis[
            "recurring_components"
        ]
    )

    for item in recurring[:3]:
        latest = (
            item.get(
                "latest_date"
            )
        )

        evidence = (
            f"Recorded on "
            f"{item['test_count']} separate "
            f"MOT tests"
        )

        if latest:
            evidence += (
                f", most recently {latest}"
            )

        result.append(
            AiInsightItem(
                title=(
                    f"Recurring "
                    f"{item['label'].lower()}"
                ),

                detail=(
                    f"{item['label']} appears "
                    f"across multiple recent "
                    f"MOT tests, making it a "
                    f"recurring recorded area "
                    f"worth noting."
                ),

                level="watch",

                evidence=(
                    evidence
                    + "."
                ),
            )
        )

    if (
        stats["failed"] > 0
        and len(result) < 3
    ):
        result.append(
            AiInsightItem(
                title="Recent MOT failures",

                detail=(
                    "The recent MOT history "
                    "contains failed tests, so "
                    "the associated recorded "
                    "defects are worth reviewing "
                    "alongside later passes."
                ),

                level="watch",

                evidence=(
                    f"{stats['failed']} failed "
                    f"MOT test"
                    + (
                        "s."
                        if stats["failed"] != 1
                        else "."
                    )
                ),
            )
        )

    if (
        (
            stats["major"] > 0
            or stats["dangerous"] > 0
        )
        and len(result) < 3
    ):
        result.append(
            AiInsightItem(
                title=(
                    "Significant recorded defects"
                ),

                detail=(
                    "The recent MOT record "
                    "contains defects above "
                    "advisory level."
                ),

                level="attention",

                evidence=(
                    f"{stats['major']} major and "
                    f"{stats['dangerous']} "
                    f"dangerous recorded defects."
                ),
            )
        )

    if not result:
        result.append(
            AiInsightItem(
                title="Recent MOT pattern",

                detail=(
                    "The supplied recent MOT "
                    "history does not contain a "
                    "strong recurring component "
                    "pattern from the categories "
                    "identified by MyGarage."
                ),

                level="info",

                evidence=(
                    f"{stats['tests']} recent "
                    f"MOT tests analysed."
                ),
            )
        )

    return result[:3]


def _fallback_narrative(
    context: dict[str, Any],
) -> AiGeneratedNarrative:
    return AiGeneratedNarrative(
        overall_tone=(
            _fallback_tone(
                context
            )
        ),

        summary=(
            _fallback_summary(
                context
            )
        ),

        insights=(
            _fallback_insights(
                context
            )
        ),

        mileage_analysis=(
            _fallback_mileage(
                context
            )
        ),

        supplementary_note=None,
    )


def _build_narrative(
    text: str,
    context: dict[str, Any],
) -> AiGeneratedNarrative:
    parsed = (
        _parse_tagged_output(
            text
        )
    )

    fallback = (
        _fallback_narrative(
            context
        )
    )

    tone = (
        parsed
        .get(
            "TONE",
            "",
        )
        .lower()
        .strip()
    )

    if tone not in VALID_TONES:
        tone = (
            fallback
            .overall_tone
        )

    insights: list[
        AiInsightItem
    ] = []

    for index in range(
        1,
        4,
    ):
        title = (
            parsed.get(
                f"INSIGHT_{index}_TITLE",
                "",
            )
            .strip()
        )

        detail = (
            parsed.get(
                f"INSIGHT_{index}_DETAIL",
                "",
            )
            .strip()
        )

        evidence = (
            parsed.get(
                f"INSIGHT_{index}_EVIDENCE",
                "",
            )
            .strip()
        )

        level = (
            parsed.get(
                f"INSIGHT_{index}_LEVEL",
                "",
            )
            .lower()
            .strip()
        )

        if (
            not title
            or not detail
            or not evidence
        ):
            continue

        if level not in VALID_LEVELS:
            level = "info"

        insights.append(
            AiInsightItem(
                title=title,
                detail=detail,
                level=level,
                evidence=evidence,
            )
        )

    if len(insights) < 3:
        existing_titles = {
            item.title.lower()
            for item in insights
        }

        for fallback_item in (
            fallback.insights
        ):
            if len(insights) >= 3:
                break

            if (
                fallback_item
                .title
                .lower()
                in existing_titles
            ):
                continue

            insights.append(
                fallback_item
            )

            existing_titles.add(
                fallback_item
                .title
                .lower()
            )

    supplementary = (
        parsed
        .get(
            "SUPPLEMENTARY",
            "",
        )
        .strip()
    )

    if (
        not supplementary
        or supplementary.upper()
        == "NONE"
        or (
            "supplementary_user_records"
            not in context
        )
    ):
        supplementary = None

    return AiGeneratedNarrative(
        overall_tone=tone,

        summary=(
            parsed.get(
                "SUMMARY",
                "",
            ).strip()
            or fallback.summary
        ),

        insights=(
            insights[:3]
        ),

        mileage_analysis=(
            parsed.get(
                "MILEAGE",
                "",
            ).strip()
            or (
                fallback
                .mileage_analysis
            )
        ),

        supplementary_note=(
            supplementary
        ),
    )


class VehicleAiService:
    def __init__(
        self,
        provider: AiProvider,
    ) -> None:
        self.provider = provider

    def status(
        self,
    ) -> AiStatusRead:
        available, message = (
            self.provider
            .check_status()
        )

        return AiStatusRead(
            available=available,
            model=self.provider.model,
            message=message,
        )

    def generate_insights(
        self,
        vehicle: AiVehicleSnapshot,
    ) -> AiVehicleInsights:
        context = (
            build_vehicle_context(
                vehicle
            )
        )

        user_prompt = (
            "Analyse this vehicle using the "
            f"complete MOT records from the "
            f"most recent {AI_HISTORY_YEARS} "
            f"years.\n\n"
            "Every recorded item on every MOT "
            "in the supplied history must be "
            "considered.\n\n"
            "VEHICLE DATA:\n"
            + _compact_json(
                context
            )
        )

        raw_response = (
            self.provider
            .generate_text(
                system_prompt=(
                    INSIGHT_SYSTEM_PROMPT
                ),

                user_prompt=(
                    user_prompt
                ),

                num_predict=360,
            )
        )

        narrative = (
            _build_narrative(
                raw_response,
                context,
            )
        )

        return AiVehicleInsights(
            overall_tone=(
                narrative
                .overall_tone
            ),

            summary=(
                narrative.summary
            ),

            mot_stats=(
                build_mot_stats(
                    context
                )
            ),

            insights=(
                narrative.insights
            ),

            recurring_items=(
                build_recurring_items(
                    context
                )
            ),

            mileage_analysis=(
                narrative
                .mileage_analysis
            ),

            supplementary_note=(
                narrative
                .supplementary_note
            ),

            disclaimer=(
                DISCLAIMER
            ),
        )

    def answer_question(
        self,
        vehicle: AiVehicleSnapshot,
        question: str,
    ) -> AiQuestionResponse:
        context = (
            build_vehicle_context(
                vehicle
            )
        )

        user_prompt = (
            "VEHICLE DATA:\n"
            + _compact_json(
                context
            )
            + "\n\n"
            + "USER QUESTION:\n"
            + question.strip()
        )

        answer = (
            self.provider
            .generate_text(
                system_prompt=(
                    QUESTION_SYSTEM_PROMPT
                ),

                user_prompt=(
                    user_prompt
                ),

                num_predict=220,
            )
            .strip()
        )

        if not answer:
            answer = (
                "The supplied vehicle records "
                "do not provide enough "
                "information to answer that "
                "question."
            )

        return AiQuestionResponse(
            answer=answer,

            disclaimer=(
                DISCLAIMER
            ),
        )