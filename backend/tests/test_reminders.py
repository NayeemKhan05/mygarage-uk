from datetime import (
    date,
    timedelta,
)


def create_vehicle(
    authenticated_client,
) -> int:
    response = (
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
        response.status_code
        == 201
    )

    return response.json()[
        "id"
    ]


def test_reminders_require_login(
    client,
):
    response = client.get(
        "/api/v1/reminders"
    )

    assert (
        response.status_code
        == 401
    )


def test_due_soon_maintenance_creates_warning(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": (
                "Engine oil"
            ),
            "category": "oil",
            "next_due_date": (
                date.today()
                + timedelta(
                    days=10
                )
            ).isoformat(),
        },
    )

    response = (
        authenticated_client.get(
            "/api/v1/reminders"
        )
    )

    assert (
        response.status_code
        == 200
    )

    reminders = (
        response.json()
    )

    assert len(
        reminders
    ) == 1

    reminder = reminders[0]

    assert (
        reminder["kind"]
        == "maintenance"
    )

    assert (
        reminder["severity"]
        == "warning"
    )

    assert (
        reminder["title"]
        == "Engine oil"
    )


def test_overdue_maintenance_creates_urgent_reminder(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": (
                "Coolant change"
            ),
            "category": "fluids",
            "next_due_date": (
                date.today()
                - timedelta(
                    days=5
                )
            ).isoformat(),
        },
    )

    response = (
        authenticated_client.get(
            "/api/v1/reminders"
        )
    )

    reminder = (
        response.json()[0]
    )

    assert (
        reminder["severity"]
        == "urgent"
    )


def test_reminder_can_be_dismissed(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": (
                "Brake inspection"
            ),
            "category": "brakes",
            "next_due_date": (
                date.today()
                + timedelta(
                    days=5
                )
            ).isoformat(),
        },
    )

    reminders = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    reminder_key = (
        reminders[0][
            "reminder_key"
        ]
    )

    response = (
        authenticated_client.post(
            "/api/v1/reminders/dismiss",
            json={
                "reminder_key":
                    reminder_key,
            },
        )
    )

    assert (
        response.status_code
        == 204
    )

    after = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    assert after == []


def test_dismissed_reminders_can_be_restored(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": "Tyres",
            "category": "tyres",
            "next_due_date": (
                date.today()
                + timedelta(
                    days=5
                )
            ).isoformat(),
        },
    )

    reminders = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    authenticated_client.post(
        "/api/v1/reminders/dismiss",
        json={
            "reminder_key":
                reminders[0][
                    "reminder_key"
                ],
        },
    )

    response = (
        authenticated_client.delete(
            "/api/v1/reminders/dismissals"
        )
    )

    assert (
        response.status_code
        == 204
    )

    restored = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    assert len(
        restored
    ) == 1


def test_reminder_settings_can_disable_maintenance(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": (
                "Engine oil"
            ),
            "category": "oil",
            "next_due_date": (
                date.today()
                + timedelta(
                    days=5
                )
            ).isoformat(),
        },
    )

    response = (
        authenticated_client.put(
            "/api/v1/reminders/settings",
            json={
                "maintenance_enabled":
                    False,
            },
        )
    )

    assert (
        response.status_code
        == 200
    )

    reminders = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    assert reminders == []


def test_due_soon_window_is_configurable(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    authenticated_client.post(
        (
            f"/api/v1/vehicles/"
            f"{vehicle_id}/maintenance"
        ),
        json={
            "name": (
                "Brake fluid"
            ),
            "category": "fluids",
            "next_due_date": (
                date.today()
                + timedelta(
                    days=20
                )
            ).isoformat(),
        },
    )

    first = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    assert len(
        first
    ) == 1

    authenticated_client.put(
        "/api/v1/reminders/settings",
        json={
            "due_soon_days": 7,
        },
    )

    second = (
        authenticated_client.get(
            "/api/v1/reminders"
        ).json()
    )

    assert second == []