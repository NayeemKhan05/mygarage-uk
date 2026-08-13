from app.schemas.dvsa import DvsaVehicle
from app.services.dvsa_client import (
    DvsaVehicleNotFoundError,
)


class FakeDvsaClient:
    def get_vehicle_by_registration(
        self,
        registration: str,
    ) -> DvsaVehicle:
        return DvsaVehicle.model_validate(
            {
                "registration": registration,
                "make": "NISSAN",
                "model": "QASHQAI",
                "fuelType": "Petrol",
                "engineSize": 1598,
                "primaryColour": "Black",
                "manufactureDate": "2012-01-01",
                "motTests": [
                    {
                        "completedDate": "2024-08-10 09:15:00",
                        "motTestNumber": 111111111111,
                        "dataSource": "dvsa",
                        "expiryDate": "2025-08-09",
                        "registrationAtTimeOfTest": "EJ62WZP",
                        "testResult": "PASSED",
                        "odometerValue": "82000",
                        "odometerUnit": "MI",
                        "odometerResultType": "READ",
                        "defects": [
                            {
                                "dangerous": False,
                                "text": (
                                    "Nearside front tyre "
                                    "worn close to legal limit"
                                ),
                                "type": "ADVISORY",
                            }
                        ],
                    },
                    {
                        "completedDate": "2025-08-09 10:30:00",
                        "motTestNumber": 222222222222,
                        "dataSource": "dvsa",
                        "expiryDate": "2026-08-08",
                        "registrationAtTimeOfTest": "EJ62WZP",
                        "testResult": "PASSED",
                        "odometerValue": "89500",
                        "odometerUnit": "MI",
                        "odometerResultType": "READ",
                        "defects": [],
                    },
                ],
            }
        )


class MissingVehicleDvsaClient:
    def get_vehicle_by_registration(
        self,
        registration: str,
    ) -> DvsaVehicle:
        raise DvsaVehicleNotFoundError()