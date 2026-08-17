from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


MaintenanceCategory = Literal[
    "oil",
    "filters",
    "brakes",
    "tyres",
    "fluids",
    "belts",
    "battery",
    "suspension",
    "general",
    "other",
]


MaintenanceStatus = Literal[
    "good",
    "due_soon",
    "overdue",
    "unknown",
]


class MaintenanceItemCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=160,
    )

    category: MaintenanceCategory

    last_completed_date: date | None = None

    last_completed_mileage: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
    )

    next_due_date: date | None = None

    next_due_mileage: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )


class MaintenanceItemUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=160,
    )

    category: MaintenanceCategory | None = None

    last_completed_date: date | None = None

    last_completed_mileage: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
    )

    next_due_date: date | None = None

    next_due_mileage: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )


class MaintenanceItemRead(BaseModel):
    id: int
    vehicle_id: int

    name: str
    category: str

    last_completed_date: date | None
    last_completed_mileage: int | None

    next_due_date: date | None
    next_due_mileage: int | None

    notes: str | None

    status: MaintenanceStatus
    status_reason: str

    current_mileage: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )