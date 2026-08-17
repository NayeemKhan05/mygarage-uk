def test_create_vehicle(
    authenticated_client,
):
    response = authenticated_client.post(
        "/api/v1/vehicles",
        json={
            "registration": "AB12 CDE",
            "make": "Honda",
            "model": "Civic",
            "fuel_type": "Petrol",
            "engine_size": 1590,
            "colour": "Silver",
            "year": 2002,
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["registration"] == "AB12CDE"


def test_list_vehicles(
    authenticated_client,
):
    authenticated_client.post(
        "/api/v1/vehicles",
        json={
            "registration": "AB12 CDE",
            "make": "Honda",
            "model": "Civic",
        },
    )

    response = authenticated_client.get(
        "/api/v1/vehicles",
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_vehicle_is_rejected(
    authenticated_client,
):
    vehicle = {
        "registration": "AB12 CDE",
        "make": "Honda",
        "model": "Civic",
    }

    first_response = authenticated_client.post(
        "/api/v1/vehicles",
        json=vehicle,
    )

    second_response = authenticated_client.post(
        "/api/v1/vehicles",
        json=vehicle,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_unknown_vehicle_returns_404(
    authenticated_client,
):
    response = authenticated_client.get(
        "/api/v1/vehicles/999",
    )

    assert response.status_code == 404


def test_vehicle_routes_require_login(
    client,
):
    response = client.get(
        "/api/v1/vehicles",
    )

    assert response.status_code == 401