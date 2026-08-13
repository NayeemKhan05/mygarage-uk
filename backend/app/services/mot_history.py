from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mot import MotDefect, MotTest
from app.models.vehicle import Vehicle
from app.schemas.dvsa import DvsaMotTest
from app.schemas.mot import MotDefectRead, MotTestRead


def parse_odometer_value(
    value: str | int | None,
) -> int | None:
    if value is None:
        return None

    value_as_text = (
        str(value)
        .strip()
        .replace(",", "")
    )

    if not value_as_text.isdigit():
        return None

    return int(value_as_text)


def sort_dvsa_mot_tests(
    mot_tests: list[DvsaMotTest],
) -> list[DvsaMotTest]:
    return sorted(
        mot_tests,
        key=lambda test: test.completed_at,
        reverse=True,
    )


def dvsa_mot_test_to_read(
    test: DvsaMotTest,
) -> MotTestRead:
    return MotTestRead(
        mot_test_number=str(
            test.mot_test_number
        ),
        completed_at=test.completed_at,
        data_source=test.data_source,
        expiry_date=test.expiry_date,
        registration_at_time_of_test=(
            test.registration_at_time_of_test
        ),
        test_result=test.test_result,
        odometer_value=parse_odometer_value(
            test.odometer_value
        ),
        odometer_unit=(
            test.odometer_unit.upper()
            if test.odometer_unit
            else None
        ),
        odometer_result_type=(
            test.odometer_result_type
        ),
        defects=[
            MotDefectRead(
                text=defect.text,
                type=defect.type.upper(),
                dangerous=defect.dangerous,
            )
            for defect in test.defects
        ],
    )


def save_mot_history(
    db: Session,
    vehicle: Vehicle,
    mot_tests: list[DvsaMotTest],
) -> int:
    if vehicle.id is None:
        raise RuntimeError(
            "Vehicle must be saved before importing MOT history"
        )

    existing_test_numbers = set(
        db.scalars(
            select(MotTest.mot_test_number).where(
                MotTest.vehicle_id == vehicle.id
            )
        ).all()
    )

    saved_count = 0

    for test in sort_dvsa_mot_tests(mot_tests):
        mot_test_number = str(
            test.mot_test_number
        ).strip()

        if mot_test_number in existing_test_numbers:
            continue

        mot_test = MotTest(
            vehicle_id=vehicle.id,
            mot_test_number=mot_test_number,
            completed_at=test.completed_at,
            data_source=test.data_source,
            expiry_date=test.expiry_date,
            registration_at_time_of_test=(
                test.registration_at_time_of_test
            ),
            test_result=(
                test.test_result.upper()
                if test.test_result
                else None
            ),
            odometer_value=parse_odometer_value(
                test.odometer_value
            ),
            odometer_unit=(
                test.odometer_unit.upper()
                if test.odometer_unit
                else None
            ),
            odometer_result_type=(
                test.odometer_result_type
            ),
        )

        mot_test.defects = [
            MotDefect(
                text=defect.text,
                type=defect.type.upper(),
                dangerous=defect.dangerous,
            )
            for defect in test.defects
        ]

        db.add(mot_test)

        existing_test_numbers.add(
            mot_test_number
        )

        saved_count += 1

    return saved_count