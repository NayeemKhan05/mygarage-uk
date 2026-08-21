def check_payload(
    registration: str = "AB12CDE",
) -> dict:
    return {
        "registration": registration,
        "make": "Honda",
        "model": "Civic",
        "fuel_type": "Petrol",
        "colour": "White",
        "year": 2012,
    }


def test_anonymous_check_history_is_not_saved(
    client,
):
    response = client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(),
    )

    assert response.status_code == 200
    assert response.json() is None

    history_response = client.get(
        "/api/v1/vehicle-checks/history"
    )

    assert (
        history_response.status_code
        == 401
    )


def test_authenticated_user_can_save_check(
    authenticated_client,
):
    response = authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(),
    )

    assert response.status_code == 200

    result = response.json()

    assert (
        result["registration"]
        == "AB12CDE"
    )

    assert result["make"] == "Honda"
    assert result["model"] == "Civic"

    assert result["check_count"] == 1
    assert result["in_garage"] is False

    history_response = (
        authenticated_client.get(
            "/api/v1/vehicle-checks/history"
        )
    )

    assert (
        history_response.status_code
        == 200
    )

    assert (
        len(
            history_response.json()
        )
        == 1
    )


def test_repeated_check_updates_existing_entry(
    authenticated_client,
):
    authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(),
    )

    second_payload = (
        check_payload()
    )

    second_payload["colour"] = "Blue"

    response = authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=second_payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["check_count"] == 2
    assert result["colour"] == "Blue"

    history_response = (
        authenticated_client.get(
            "/api/v1/vehicle-checks/history"
        )
    )

    history = (
        history_response.json()
    )

    assert len(history) == 1
    assert history[0]["check_count"] == 2


def test_registration_is_normalised(
    authenticated_client,
):
    response = authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(
            "ab12 cde"
        ),
    )

    assert response.status_code == 200

    assert (
        response.json()["registration"]
        == "AB12CDE"
    )


def test_history_detects_vehicle_in_garage(
    authenticated_client,
):
    vehicle_response = (
        authenticated_client.post(
            "/api/v1/vehicles",
            json={
                "registration": "AB12CDE",
                "make": "Honda",
                "model": "Civic",
            },
        )
    )

    assert (
        vehicle_response.status_code
        == 201
    )

    vehicle_id = (
        vehicle_response.json()["id"]
    )

    authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(),
    )

    response = (
        authenticated_client.get(
            "/api/v1/vehicle-checks/history"
        )
    )

    item = response.json()[0]

    assert item["in_garage"] is True

    assert (
        item["garage_vehicle_id"]
        == vehicle_id
    )


def test_user_can_delete_history_item(
    authenticated_client,
):
    create_response = (
        authenticated_client.post(
            "/api/v1/vehicle-checks/history",
            json=check_payload(),
        )
    )

    check_id = (
        create_response.json()["id"]
    )

    delete_response = (
        authenticated_client.delete(
            (
                "/api/v1/vehicle-checks/"
                f"history/{check_id}"
            )
        )
    )

    assert (
        delete_response.status_code
        == 204
    )

    history_response = (
        authenticated_client.get(
            "/api/v1/vehicle-checks/history"
        )
    )

    assert (
        history_response.json()
        == []
    )


def test_user_can_clear_history(
    authenticated_client,
):
    authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(
            "AB12CDE"
        ),
    )

    authenticated_client.post(
        "/api/v1/vehicle-checks/history",
        json=check_payload(
            "XY34ZAB"
        ),
    )

    response = (
        authenticated_client.delete(
            "/api/v1/vehicle-checks/history"
        )
    )

    assert response.status_code == 204

    history_response = (
        authenticated_client.get(
            "/api/v1/vehicle-checks/history"
        )
    )

    assert (
        history_response.json()
        == []
    )