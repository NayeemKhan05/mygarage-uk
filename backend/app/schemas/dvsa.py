from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DvsaVehicle(BaseModel):
    registration: str

    make: str | None = None
    model: str | None = None

    fuel_type: str | None = Field(
        default=None,
        alias="fuelType",
    )

    engine_size: int | None = Field(
        default=None,
        alias="engineSize",
    )

    primary_colour: str | None = Field(
        default=None,
        alias="primaryColour",
    )

    first_used_date: date | None = Field(
        default=None,
        alias="firstUsedDate",
    )

    registration_date: date | None = Field(
        default=None,
        alias="registrationDate",
    )

    manufacture_date: date | None = Field(
        default=None,
        alias="manufactureDate",
    )

    mot_tests: list[dict[str, Any]] = Field(
        default_factory=list,
        alias="motTests",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )