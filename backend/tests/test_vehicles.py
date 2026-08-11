def test_create_vehicle(client):
    response = client.post(
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

    vehicle = response.json()

    assert vehicle["registration"] == "AB12CDE"
    assert vehicle["make"] == "Honda"
    assert vehicle["model"] == "Civic"
    assert vehicle["id"] == 1


def test_list_vehicles(client):
    client.post(
        "/api/v1/vehicles",
        json={
            "registration": "AB12 CDE",
            "make": "Honda",
            "model": "Civic",
        },
    )

    response = client.get("/api/v1/vehicles")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_registration_is_rejected(client):
    vehicle = {
        "registration": "AB12 CDE",
        "make": "Honda",
        "model": "Civic",
    }

    first_response = client.post("/api/v1/vehicles", json=vehicle)
    second_response = client.post("/api/v1/vehicles", json=vehicle)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_get_unknown_vehicle_returns_404(client):
    response = client.get("/api/v1/vehicles/999")

    assert response.status_code == 404