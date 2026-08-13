from app.main import app
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


def test_import_vehicle_and_mot_history(client):
    use_fake_dvsa()

    try:
        response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "ej62 wzp",
            },
        )
    finally:
        clear_fake_dvsa()

    assert response.status_code == 201

    result = response.json()

    assert (
        result["vehicle"]["registration"]
        == "EJ62WZP"
    )

    assert result["vehicle"]["make"] == "NISSAN"
    assert result["vehicle"]["model"] == "QASHQAI"

    assert result["mot_tests_found"] == 2
    assert result["mot_tests_saved"] == 2


def test_imported_mot_history_can_be_retrieved(client):
    use_fake_dvsa()

    try:
        import_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62WZP",
            },
        )
    finally:
        clear_fake_dvsa()

    vehicle_id = (
        import_response.json()["vehicle"]["id"]
    )

    response = client.get(
        f"/api/v1/vehicles/{vehicle_id}/mot-history"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2

    # The newest MOT should come first.
    assert (
        history[0]["mot_test_number"]
        == "222222222222"
    )

    assert history[0]["odometer_value"] == 89500

    assert len(history[1]["defects"]) == 1

    assert (
        history[1]["defects"][0]["type"]
        == "ADVISORY"
    )


def test_refresh_does_not_duplicate_mot_tests(client):
    use_fake_dvsa()

    try:
        import_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62WZP",
            },
        )

        vehicle_id = (
            import_response.json()["vehicle"]["id"]
        )

        refresh_response = client.post(
            f"/api/v1/vehicles/"
            f"{vehicle_id}/mot-history/refresh"
        )

    finally:
        clear_fake_dvsa()

    assert refresh_response.status_code == 200

    result = refresh_response.json()

    assert result["mot_tests_found"] == 2
    assert result["mot_tests_saved"] == 0


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
        clear_fake_dvsa()

    assert response.status_code == 404


def test_duplicate_vehicle_returns_409(client):
    use_fake_dvsa()

    try:
        first_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62WZP",
            },
        )

        second_response = client.post(
            "/api/v1/vehicles/import",
            json={
                "registration": "EJ62WZP",
            },
        )
    finally:
        clear_fake_dvsa()

    assert first_response.status_code == 201
    assert second_response.status_code == 409