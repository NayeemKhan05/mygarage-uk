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
    text: str = Field(
        min_length=1,
        max_length=1200,
    )

    type: str | None = Field(
        default=None,
        max_length=50,
    )

    dangerous: bool = False


class AiMotTestInput(BaseModel):
    completed_at: datetime | None = None

    test_result: str | None = Field(
        default=None,
        max_length=50,
    )

    expiry_date: date | None = None

    odometer_value: int | None = Field(
        default=None,
        ge=0,
    )

    odometer_unit: str | None = Field(
        default=None,
        max_length=30,
    )

    mot_test_number: str | None = Field(
        default=None,
        max_length=100,
    )

    defects: list[AiDefectInput] = Field(
        default_factory=list,
        max_length=40,
    )


class AiVehicleSnapshot(BaseModel):
    registration: str = Field(
        min_length=1,
        max_length=12,
    )

    make: str | None = Field(
        default=None,
        max_length=100,
    )

    model: str | None = Field(
        default=None,
        max_length=100,
    )

    fuel_type: str | None = Field(
        default=None,
        max_length=50,
    )

    engine_size: int | None = Field(
        default=None,
        ge=0,
    )

    colour: str | None = Field(
        default=None,
        max_length=50,
    )

    year: int | None = Field(
        default=None,
        ge=1886,
        le=3000,
    )

    mot_tests: list[AiMotTestInput] = Field(
        default_factory=list,
        max_length=50,
    )

    supplementary_service_records: list[dict[str, Any]] = Field(
        default_factory=list,
        max_length=25,
    )

    supplementary_maintenance_items: list[dict[str, Any]] = Field(
        default_factory=list,
        max_length=25,
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
    tests: int = Field(
        ge=0,
    )

    passed: int = Field(
        ge=0,
    )

    failed: int = Field(
        ge=0,
    )

    recorded_items: int = Field(
        ge=0,
    )

    dangerous: int = Field(
        ge=0,
    )

    major: int = Field(
        ge=0,
    )

    minor: int = Field(
        ge=0,
    )

    advisory: int = Field(
        ge=0,
    )

    prs: int = Field(
        ge=0,
    )

    mileage_points: int = Field(
        ge=0,
    )

    mileage_decreases: int = Field(
        ge=0,
    )


class AiInsightItem(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=120,
    )

    detail: str = Field(
        min_length=1,
        max_length=700,
    )

    level: AiInsightLevel

    evidence: str = Field(
        min_length=1,
        max_length=500,
    )


class AiRecurringItem(BaseModel):
    label: str = Field(
        min_length=1,
        max_length=180,
    )

    count: int = Field(
        ge=2,
    )

    latest_date: str | None = Field(
        default=None,
        max_length=40,
    )


class AiGeneratedNarrative(BaseModel):
    overall_tone: AiTone

    summary: str = Field(
        min_length=1,
        max_length=1000,
    )

    insights: list[AiInsightItem] = Field(
        default_factory=list,
        max_length=4,
    )

    mileage_analysis: str = Field(
        min_length=1,
        max_length=700,
    )

    supplementary_note: str | None = Field(
        default=None,
        max_length=500,
    )


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
    answer: str = Field(
        min_length=1,
        max_length=1800,
    )


class AiQuestionResponse(BaseModel):
    answer: str

    disclaimer: str


class AiStatusRead(BaseModel):
    available: bool

    model: str

    message: str