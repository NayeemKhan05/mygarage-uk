from datetime import (
    date,
    timedelta,
)


def create_vehicle(
    authenticated_client,
) -> int:
    response = authenticated_client.post(
        "/api/v1/vehicles",
        json={
            "registration": "AB12CDE",
            "make": "Honda",
            "model": "Civic",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_maintenance_item_can_be_created(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    response = authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": "Engine oil",
            "category": "oil",
            "last_completed_date": (
                "2026-05-01"
            ),
            "last_completed_mileage": 80000,
            "next_due_date": (
                date.today()
                + timedelta(days=120)
            ).isoformat(),
            "next_due_mileage": 90000,
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["name"] == "Engine oil"
    assert result["status"] == "good"


def test_maintenance_due_soon(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    response = authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": "Brake inspection",
            "category": "brakes",
            "next_due_date": (
                date.today()
                + timedelta(days=10)
            ).isoformat(),
        },
    )

    assert response.status_code == 201

    assert (
        response.json()["status"]
        == "due_soon"
    )


def test_maintenance_overdue(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    response = authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": "Coolant change",
            "category": "fluids",
            "next_due_date": (
                date.today()
                - timedelta(days=10)
            ).isoformat(),
        },
    )

    assert response.status_code == 201

    assert (
        response.json()["status"]
        == "overdue"
    )


def test_maintenance_without_due_target_is_unknown(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    response = authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": "Battery",
            "category": "battery",
        },
    )

    assert response.status_code == 201

    assert (
        response.json()["status"]
        == "unknown"
    )


def test_maintenance_item_can_be_deleted(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    create_response = (
        authenticated_client.post(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/maintenance"
            ),
            json={
                "name": "Tyres",
                "category": "tyres",
            },
        )
    )

    item_id = (
        create_response.json()["id"]
    )

    response = (
        authenticated_client.delete(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/maintenance/"
                f"{item_id}"
            )
        )
    )

    assert response.status_code == 204