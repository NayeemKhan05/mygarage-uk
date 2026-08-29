import json

from app.schemas.ai import (
    AiGeneratedNarrative,
    AiQuestionGenerated,
    AiQuestionResponse,
    AiStatusRead,
    AiVehicleInsights,
    AiVehicleSnapshot,
)
from app.services.ai_context import (
    build_mot_stats,
    build_recurring_items,
    build_vehicle_context,
)
from app.services.ai_provider import (
    AiProvider,
)


INSIGHT_SYSTEM_PROMPT = """
You are MyGarage UK's local vehicle-history assistant.

Analyse only the supplied evidence.

DVSA MOT data is the primary evidence.
Statistics and recurring-item counts were calculated by the backend and
are authoritative.

User-entered service or maintenance records, if present, are supplementary
and may be incomplete.

Rules:
- Never criticise missing service or maintenance records.
- Never infer neglect from missing user-entered information.
- Never invent defects, repairs, dates, mileage or counts.
- Do not diagnose mechanical faults.
- Do not predict component failure.
- A passed MOT does not prove perfect mechanical condition.
- A mileage decrease is a recorded inconsistency, not proof of clocking.
- Do not give an unsupported buy or don't-buy verdict.
- Use British English.
- Be concise.
- Prefer specific MOT evidence over general automotive advice.

Produce no more than three insight cards.

The summary should be roughly 2 to 4 sentences.
Each insight detail should normally be 1 to 2 sentences.
Mileage analysis should normally be 1 to 3 sentences.
"""


QUESTION_SYSTEM_PROMPT = """
You are MyGarage UK's local vehicle-history assistant.

Answer using only the supplied evidence.

DVSA MOT history is the primary evidence.
Backend-calculated statistics are authoritative.

User-entered service and maintenance records, if supplied, may be
incomplete and are supplementary only.

Never infer poor maintenance from missing user-entered records.

Never invent:
- defects
- repairs
- dates
- mileages
- services
- MOT results
- exact counts

Do not diagnose faults.
Do not guarantee reliability.
Do not claim clocking from a mileage decrease alone.
Do not give unsupported buying verdicts.

If the records cannot answer the question, say so.

Use British English.
Answer concisely, normally under 120 words.
"""


DISCLAIMER = (
    "AI-generated interpretation of the supplied "
    "vehicle records. It is not a mechanical "
    "inspection, diagnosis or guarantee of "
    "vehicle condition."
)


def _compact_json(
    value: dict,
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
            "Analyse this vehicle's MOT history.\n"
            "Use the deterministic statistics exactly as supplied.\n\n"
            + _compact_json(
                context
            )
        )

        narrative = (
            self.provider
            .generate_structured(
                system_prompt=(
                    INSIGHT_SYSTEM_PROMPT
                ),
                user_prompt=(
                    user_prompt
                ),
                response_model=(
                    AiGeneratedNarrative
                ),
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
                narrative.insights[
                    :3
                ]
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
            "VEHICLE EVIDENCE:\n"
            + _compact_json(
                context
            )
            + "\n\nQUESTION:\n"
            + question.strip()
        )

        generated = (
            self.provider
            .generate_structured(
                system_prompt=(
                    QUESTION_SYSTEM_PROMPT
                ),
                user_prompt=(
                    user_prompt
                ),
                response_model=(
                    AiQuestionGenerated
                ),
            )
        )

        return AiQuestionResponse(
            answer=(
                generated.answer
            ),

            disclaimer=(
                DISCLAIMER
            ),
        )