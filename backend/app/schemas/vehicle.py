from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.schemas.mot import MotTestRead


def normalise_registration(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Registration must be a string")

    registration = "".join(
        value.upper().split()
    )

    if not registration:
        raise ValueError("Registration cannot be empty")

    if len(registration) > 8:
        raise ValueError("Registration is too long")

    if not registration.isalnum():
        raise ValueError(
            "Registration must only contain letters and numbers"
        )

    return registration


class VehicleRegistration(BaseModel):
    registration: str = Field(
        min_length=1,
        max_length=8,
    )

    @field_validator(
        "registration",
        mode="before",
    )
    @classmethod
    def validate_registration(
        cls,
        value: str,
    ) -> str:
        return normalise_registration(value)


class VehicleBase(VehicleRegistration):
    make: str = Field(
        min_length=1,
        max_length=100,
    )

    model: str = Field(
        min_length=1,
        max_length=100,
    )

    fuel_type: str | None = Field(
        default=None,
        max_length=50,
    )

    engine_size: int | None = Field(
        default=None,
        gt=0,
    )

    colour: str | None = Field(
        default=None,
        max_length=50,
    )

    year: int | None = Field(
        default=None,
        ge=1886,
        le=2100,
    )


class VehicleCreate(VehicleBase):
    pass


class VehicleLookupRequest(VehicleRegistration):
    pass


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class VehicleImportResponse(BaseModel):
    vehicle: VehicleRead
    mot_tests_found: int
    mot_tests_saved: int


class VehicleCheckResponse(VehicleBase):
    mot_tests_found: int
    mot_tests: list[MotTestRead]

    in_garage: bool
    garage_vehicle_id: int | None = None