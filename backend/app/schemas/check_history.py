from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class VehicleCheckHistoryCreate(BaseModel):
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

    colour: str | None = Field(
        default=None,
        max_length=50,
    )

    year: int | None = Field(
        default=None,
        ge=1886,
        le=3000,
    )

    @field_validator("registration")
    @classmethod
    def normalise_registration(
        cls,
        value: str,
    ) -> str:
        registration = (
            value
            .replace(" ", "")
            .upper()
            .strip()
        )

        if not registration:
            raise ValueError(
                "Registration cannot be empty"
            )

        return registration


class VehicleCheckHistoryRead(BaseModel):
    id: int

    registration: str

    make: str | None
    model: str | None

    fuel_type: str | None
    colour: str | None
    year: int | None

    first_checked_at: datetime
    last_checked_at: datetime

    in_garage: bool = False
    garage_vehicle_id: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )