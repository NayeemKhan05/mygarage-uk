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
You are the AI Vehicle Insights feature for MyGarage UK.

You analyse structured UK vehicle records.

EVIDENCE PRIORITY

1. DVSA MOT history is the primary evidence.
2. Backend-calculated MOT statistics and recurring-component counts are
   deterministic and should be trusted.
3. User-entered service records and maintenance schedules, when present,
   are supplementary only.
4. User-entered records may be incomplete.

STRICT RULES

- Never infer poor maintenance, neglect or poor servicing because service
  records or maintenance records are absent.
- Never describe missing MyGarage service records as a negative finding.
- Never claim the supplied user-entered service history is complete.
- Do not invent MOT defects, dates, mileages, repairs or counts.
- Do not recount deterministic statistics differently.
- Focus on recorded MOT patterns, advisories, failures, defect categories
  and mileage trends.
- A passed MOT does not prove a vehicle is mechanically perfect.
- Do not diagnose mechanical faults.
- Do not predict component failure.
- Do not claim a vehicle has been clocked if mileage decreases. You may
  neutrally state that the recorded mileage decreased and that the record
  would need checking.
- Do not make accident-history claims.
- Do not give a simplistic buy/don't-buy verdict.
- Distinguish recorded evidence from interpretation.
- Use British English.
- Keep the answer concise and practical.

OVERALL TONE

positive:
The supplied MOT record contains relatively few notable concerns.

neutral:
The record is mixed or does not justify a stronger judgement.

watch:
There are recurring or repeated recorded patterns worth monitoring.

attention:
The supplied MOT history contains significant repeated failures,
dangerous/major defects, or another clearly important recorded pattern.

Return only the requested structured response.
"""


QUESTION_SYSTEM_PROMPT = """
You answer questions about a vehicle in MyGarage UK.

Use only the supplied vehicle evidence.

DVSA MOT history is the primary evidence.

Backend-calculated MOT statistics are deterministic.

User-entered service and maintenance information, if supplied, is
supplementary and may be incomplete.

Never infer poor servicing or neglect from missing user-entered data.

Never invent:
- defects
- repairs
- dates
- mileages
- service events
- MOT results
- exact counts

Do not diagnose mechanical faults.
Do not guarantee future reliability.
Do not claim a vehicle has been clocked solely because a recorded mileage
decreased.
Do not give an unsupported buy/don't-buy verdict.

If the records cannot answer the question, say so.

Use British English.
Keep the answer under roughly 180 words.

Return only the requested structured response.
"""


DISCLAIMER = (
    "AI-generated interpretation of the "
    "supplied vehicle records. It is not "
    "a mechanical inspection, diagnosis "
    "or guarantee of vehicle condition."
)


class VehicleAiService:
    def __init__(
        self,
        provider:
            AiProvider,
    ):
        self.provider = (
            provider
        )


    def status(
        self,
    ) -> AiStatusRead:
        available, message = (
            self.provider
            .check_status()
        )

        return AiStatusRead(
            available=available,

            model=(
                self.provider
                .model
            ),

            message=message,
        )


    def generate_insights(
        self,
        vehicle:
            AiVehicleSnapshot,
    ) -> AiVehicleInsights:
        context = (
            build_vehicle_context(
                vehicle
            )
        )

        narrative = (
            self.provider
            .generate_structured(
                system_prompt=(
                    INSIGHT_SYSTEM_PROMPT
                ),

                user_prompt=(
                    "Analyse this vehicle "
                    "record.\n\n"
                    "VEHICLE DATA:\n"
                    + json.dumps(
                        context,
                        ensure_ascii=False,
                        default=str,
                    )
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
        vehicle:
            AiVehicleSnapshot,
        question: str,
    ) -> AiQuestionResponse:
        context = (
            build_vehicle_context(
                vehicle
            )
        )

        generated = (
            self.provider
            .generate_structured(
                system_prompt=(
                    QUESTION_SYSTEM_PROMPT
                ),

                user_prompt=(
                    "VEHICLE DATA:\n"
                    + json.dumps(
                        context,
                        ensure_ascii=False,
                        default=str,
                    )
                    + "\n\n"
                    + "USER QUESTION:\n"
                    + question.strip()
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