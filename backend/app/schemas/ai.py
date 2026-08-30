from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


AiTone = Literal[
    "positive",
    "neutral",
    "watch",
    "attention",
]


AiInsightLevel = Literal[
    "positive",
    "info",
    "watch",
    "attention",
]


class AiDefectInput(BaseModel):
    text: str

    type: str | None = None

    dangerous: bool = False


class AiMotTestInput(BaseModel):
    completed_at: datetime | None = None

    test_result: str | None = None

    expiry_date: date | None = None

    odometer_value: int | None = Field(
        default=None,
        ge=0,
    )

    odometer_unit: str | None = None

    mot_test_number: str | None = None

    defects: list[AiDefectInput] = Field(
        default_factory=list,
    )


class AiVehicleSnapshot(BaseModel):
    registration: str = Field(
        min_length=1,
        max_length=12,
    )

    make: str | None = None

    model: str | None = None

    fuel_type: str | None = None

    engine_size: int | None = Field(
        default=None,
        ge=0,
    )

    colour: str | None = None

    year: int | None = Field(
        default=None,
        ge=1886,
        le=3000,
    )

    mot_tests: list[AiMotTestInput] = Field(
        default_factory=list,
    )

    supplementary_service_records: list[
        dict[str, Any]
    ] = Field(
        default_factory=list,
    )

    supplementary_maintenance_items: list[
        dict[str, Any]
    ] = Field(
        default_factory=list,
    )

    @field_validator("registration")
    @classmethod
    def normalise_registration(
        cls,
        value: str,
    ) -> str:
        return (
            value
            .replace(" ", "")
            .upper()
            .strip()
        )


class AiInsightsRequest(BaseModel):
    vehicle: AiVehicleSnapshot


class AiQuestionRequest(BaseModel):
    vehicle: AiVehicleSnapshot

    question: str = Field(
        min_length=2,
        max_length=500,
    )


class AiMotStats(BaseModel):
    tests: int = Field(ge=0)

    passed: int = Field(ge=0)

    failed: int = Field(ge=0)

    recorded_items: int = Field(ge=0)

    dangerous: int = Field(ge=0)

    major: int = Field(ge=0)

    minor: int = Field(ge=0)

    advisory: int = Field(ge=0)

    prs: int = Field(ge=0)

    mileage_points: int = Field(ge=0)

    mileage_decreases: int = Field(ge=0)


class AiInsightItem(BaseModel):
    title: str

    detail: str

    level: AiInsightLevel

    evidence: str


class AiRecurringItem(BaseModel):
    label: str

    count: int = Field(
        ge=2,
    )

    latest_date: str | None = None


class AiGeneratedNarrative(BaseModel):
    overall_tone: AiTone

    summary: str

    insights: list[AiInsightItem] = Field(
        default_factory=list,
    )

    mileage_analysis: str

    supplementary_note: str | None = None


class AiVehicleInsights(BaseModel):
    overall_tone: AiTone

    summary: str

    mot_stats: AiMotStats

    insights: list[AiInsightItem]

    recurring_items: list[AiRecurringItem]

    mileage_analysis: str

    supplementary_note: str | None

    disclaimer: str


class AiQuestionGenerated(BaseModel):
    answer: str


class AiQuestionResponse(BaseModel):
    answer: str

    disclaimer: str


class AiStatusRead(BaseModel):
    available: bool

    model: str

    message: str