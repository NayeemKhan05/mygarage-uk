from app.main import app
from app.schemas.dvsa import DvsaVehicle
from app.services.dvsa_client import (
    DvsaVehicleNotFoundError,
    get_dvsa_client,
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
                "engineSize": "1598",
                "primaryColour": "Black",
                "firstUsedDate": "2012-09-01",
                "registrationDate": "2012-09-01",
                "manufactureDate": "2012-01-01",
                "motTests": [
                    {
                        "motTestNumber": "123456789",
                        "testResult": "PASSED",
                    },
                    {
                        "motTestNumber": "987654321",
                        "testResult": "PASSED",
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


def test_import_vehicle_from_dvsa(client):
    app.dependency_overrides[
        get_dvsa_client
    ] = lambda: FakeDvsaClient()

    try:
        response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "ej62 wzp",
            },
        )

    finally:
        app.dependency_overrides.pop(
            get_dvsa_client,
            None,
        )

    assert response.status_code == 201

    result = response.json()

    assert (
        result["vehicle"]["registration"]
        == "EJ62WZP"
    )
    assert result["vehicle"]["make"] == "NISSAN"
    assert result["vehicle"]["model"] == "QASHQAI"
    assert result["vehicle"]["engine_size"] == 1598
    assert result["vehicle"]["year"] == 2012
    assert result["mot_tests_found"] == 2


def test_imported_vehicle_is_saved(client):
    app.dependency_overrides[
        get_dvsa_client
    ] = lambda: FakeDvsaClient()

    try:
        import_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62 WZP",
            },
        )

    finally:
        app.dependency_overrides.pop(
            get_dvsa_client,
            None,
        )

    assert import_response.status_code == 201

    response = client.get(
        "/api/v1/vehicles"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert (
        response.json()[0]["registration"]
        == "EJ62WZP"
    )


def test_unknown_vehicle_returns_404(client):
    app.dependency_overrides[
        get_dvsa_client
    ] = lambda: MissingVehicleDvsaClient()

    try:
        response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "AA00AAA",
            },
        )

    finally:
        app.dependency_overrides.pop(
            get_dvsa_client,
            None,
        )

    assert response.status_code == 404


def test_duplicate_import_returns_409(client):
    app.dependency_overrides[
        get_dvsa_client
    ] = lambda: FakeDvsaClient()

    try:
        first_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62 WZP",
            },
        )

        second_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62 WZP",
            },
        )

    finally:
        app.dependency_overrides.pop(
            get_dvsa_client,
            None,
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409