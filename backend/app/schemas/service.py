from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


ServiceCategory = Literal[
    "service",
    "repair",
    "maintenance",
    "parts",
    "inspection",
    "other",
]


class ServiceRecordCreate(BaseModel):
    service_date: date

    title: str = Field(
        min_length=1,
        max_length=160,
    )

    category: ServiceCategory

    mileage: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
    )

    garage: str | None = Field(
        default=None,
        max_length=160,
    )

    cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )


class ServiceRecordUpdate(BaseModel):
    service_date: date | None = None

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=160,
    )

    category: ServiceCategory | None = None

    mileage: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
    )

    garage: str | None = Field(
        default=None,
        max_length=160,
    )

    cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )


class ServiceReceiptRead(BaseModel):
    id: int
    original_filename: str
    content_type: str
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ServiceRecordRead(BaseModel):
    id: int
    vehicle_id: int

    service_date: date
    title: str
    category: str

    mileage: int | None
    garage: str | None
    cost: float | None
    notes: str | None

    receipts: list[ServiceReceiptRead]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )