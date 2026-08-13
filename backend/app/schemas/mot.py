from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MotDefectRead(BaseModel):
    text: str
    type: str
    dangerous: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class MotTestRead(BaseModel):
    mot_test_number: str
    completed_at: datetime

    data_source: str | None
    expiry_date: date | None
    registration_at_time_of_test: str | None

    test_result: str | None

    odometer_value: int | None
    odometer_unit: str | None
    odometer_result_type: str | None

    defects: list[MotDefectRead]

    model_config = ConfigDict(
        from_attributes=True,
    )


class MotHistoryRefreshResponse(BaseModel):
    vehicle_id: int
    registration: str
    mot_tests_found: int
    mot_tests_saved: int