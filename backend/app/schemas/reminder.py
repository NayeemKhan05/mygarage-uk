from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


ReminderKind = Literal[
    "mot",
    "maintenance",
]


ReminderSeverity = Literal[
    "urgent",
    "warning",
]


class ReminderRead(BaseModel):
    reminder_key: str

    kind: ReminderKind
    severity: ReminderSeverity

    title: str
    message: str

    vehicle_id: int

    registration: str

    make: str | None
    model: str | None

    due_date: date | None = None
    due_mileage: int | None = None
    current_mileage: int | None = None

    action_href: str


class ReminderSummaryRead(BaseModel):
    total: int

    urgent: int
    warning: int

    mot: int
    maintenance: int


class ReminderSettingsRead(BaseModel):
    user_id: int

    mot_enabled: bool
    maintenance_enabled: bool

    due_soon_days: int
    due_soon_miles: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ReminderSettingsUpdate(BaseModel):
    mot_enabled: bool | None = None

    maintenance_enabled: bool | None = None

    due_soon_days: int | None = Field(
        default=None,
        ge=1,
        le=90,
    )

    due_soon_miles: int | None = Field(
        default=None,
        ge=100,
        le=5000,
    )


class ReminderDismissRequest(BaseModel):
    reminder_key: str = Field(
        min_length=1,
        max_length=255,
    )