from datetime import date, datetime

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
)


class DvsaDefect(BaseModel):
    dangerous: bool = False
    text: str = ""
    type: str

    model_config = ConfigDict(
        extra="ignore",
    )


class DvsaMotTest(BaseModel):
    mot_test_number: str | int = Field(
        alias="motTestNumber",
    )

    completed_at: datetime = Field(
        alias="completedDate",
    )

    data_source: str | None = Field(
        default=None,
        alias="dataSource",
    )

    expiry_date: date | None = Field(
        default=None,
        alias="expiryDate",
    )

    # DVSA documentation has used both names, so accepting both
    registration_at_time_of_test: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "registrationAtTimeOfTest",
            "regMarkTimeOfTest",
        ),
    )

    test_result: str | None = Field(
        default=None,
        alias="testResult",
    )

    odometer_value: str | int | None = Field(
        default=None,
        alias="odometerValue",
    )

    odometer_unit: str | None = Field(
        default=None,
        alias="odometerUnit",
    )

    odometer_result_type: str | None = Field(
        default=None,
        alias="odometerResultType",
    )

    defects: list[DvsaDefect] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


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

    mot_tests: list[DvsaMotTest] = Field(
        default_factory=list,
        alias="motTests",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def year(self) -> int | None:
        vehicle_date = (
            self.manufacture_date
            or self.first_used_date
            or self.registration_date
        )

        return vehicle_date.year if vehicle_date else None