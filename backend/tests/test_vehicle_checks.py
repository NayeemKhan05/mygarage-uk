from sqlalchemy import select

from app.main import app
from app.models.vehicle import Vehicle
from app.services.dvsa_client import (
    get_dvsa_client,
)
from tests.fakes import (
    FakeDvsaClient,
    MissingVehicleDvsaClient,
)


def use_fake_dvsa():
    app.dependency_overrides[
        get_dvsa_client
    ] = lambda: FakeDvsaClient()


def clear_fake_dvsa():
    app.dependency_overrides.pop(
        get_dvsa_client,
        None,
    )


def test_vehicle_check_returns_full_history(
    client,
):
    use_fake_dvsa()

    try:
        response = client.post(
            "/api/v1/vehicle-checks",
            json={
                "registration": "ej62 wzp",
            },
        )
    finally:
        clear_fake_dvsa()

    assert response.status_code == 200

    result = response.json()

    assert result["registration"] == "EJ62WZP"
    assert result["make"] == "NISSAN"
    assert result["mot_tests_found"] == 2
    assert result["in_garage"] is False


def test_vehicle_check_does_not_save_vehicle(
    client,
    db_session,
):
    use_fake_dvsa()

    try:
        response = client.post(
            "/api/v1/vehicle-checks",
            json={
                "registration": "EJ62WZP",
            },
        )
    finally:
        clear_fake_dvsa()

    assert response.status_code == 200

    vehicles = db_session.scalars(
        select(Vehicle)
    ).all()

    assert vehicles == []


def test_check_knows_when_vehicle_is_in_garage(
    authenticated_client,
):
    use_fake_dvsa()

    try:
        import_response = authenticated_client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62WZP",
            },
        )

        check_response = authenticated_client.post(
            "/api/v1/vehicle-checks",
            json={
                "registration": "EJ62WZP",
            },
        )

    finally:
        clear_fake_dvsa()

    vehicle_id = (
        import_response.json()["vehicle"]["id"]
    )

    result = check_response.json()

    assert result["in_garage"] is True
    assert result["garage_vehicle_id"] == vehicle_id


def test_unknown_vehicle_check_returns_404(
    client,
):
    app.dependency_overrides[
        get_dvsa_client
    ] = lambda: MissingVehicleDvsaClient()

    try:
        response = client.post(
            "/api/v1/vehicle-checks",
            json={
                "registration": "AA00AAA",
            },
        )
    finally:
        clear_fake_dvsa()

    assert response.status_code == 404