from sqlalchemy import select

from app.models.user import User
from app.models.vehicle import Vehicle


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Driver@Example.com",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["email"] == "driver@example.com"
    assert "password" not in result
    assert "password_hash" not in result

    assert (
        "mygarage_access_token"
        in response.headers["set-cookie"]
    )


def test_duplicate_email_is_rejected(client):
    payload = {
        "email": "driver@example.com",
        "password": "strongpassword123",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_with_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "strongpassword123",
        },
    )

    client.post(
        "/api/v1/auth/logout",
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "DRIVER@example.com",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["email"]
        == "driver@example.com"
    )


def test_wrong_password_is_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "strongpassword123",
        },
    )

    client.post(
        "/api/v1/auth/logout",
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "driver@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_me_returns_logged_in_user(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "strongpassword123",
        },
    )

    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 200
    assert (
        response.json()["email"]
        == "driver@example.com"
    )


def test_me_requires_login(client):
    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401


def test_logout_removes_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "strongpassword123",
        },
    )

    logout_response = client.post(
        "/api/v1/auth/logout",
    )

    assert logout_response.status_code == 204

    me_response = client.get(
        "/api/v1/auth/me",
    )

    assert me_response.status_code == 401


def test_first_account_keeps_existing_vehicles(
    client,
    db_session,
):
    vehicle = Vehicle(
        registration="AB12CDE",
        make="Honda",
        model="Civic",
        fuel_type="Petrol",
    )

    db_session.add(vehicle)
    db_session.commit()

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "strongpassword123",
        },
    )

    assert register_response.status_code == 201

    vehicles_response = client.get(
        "/api/v1/vehicles",
    )

    assert vehicles_response.status_code == 200
    assert len(
        vehicles_response.json()
    ) == 1

    assert (
        vehicles_response.json()[0]["registration"]
        == "AB12CDE"
    )


def test_password_is_not_stored_plaintext(
    client,
    db_session,
):
    password = "strongpassword123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": password,
        },
    )

    user = db_session.scalar(
        select(User).where(
            User.email
            == "driver@example.com"
        )
    )

    assert user is not None
    assert user.password_hash != password