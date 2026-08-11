from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VehicleBase(BaseModel):
    registration: str = Field(min_length=1, max_length=8)
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)

    fuel_type: str | None = Field(default=None, max_length=50)
    engine_size: int | None = Field(default=None, gt=0)
    colour: str | None = Field(default=None, max_length=50)
    year: int | None = Field(default=None, ge=1886, le=2100)

    @field_validator("registration", mode="before")
    @classmethod
    def normalise_registration(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Registration must be a string")

        # Store registrations consistently so "AB12 CDE" and "ab12cde"
        # aren't treated as two different vehicles.
        registration = "".join(value.upper().split())

        if not registration.isalnum():
            raise ValueError("Registration must only contain letters and numbers")

        return registration


class VehicleCreate(VehicleBase):
    pass


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)