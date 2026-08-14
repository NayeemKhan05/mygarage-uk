from unittest.mock import Mock, patch

from app.core.config import settings
from app.services.dvsa_client import DvsaClient


def token_response(
    token: str,
    expires_in: int = 3600,
) -> Mock:
    response = Mock()

    response.status_code = 200

    response.json.return_value = {
        "access_token": token,
        "expires_in": expires_in,
    }

    return response


def vehicle_response(
    status_code: int,
) -> Mock:
    response = Mock()

    response.status_code = status_code

    response.json.return_value = {
        "registration": "LB02BYW",
        "make": "TOYOTA",
        "model": "AVENSIS",
        "fuelType": "Petrol",
        "engineSize": 1794,
        "primaryColour": "Silver",
        "manufactureDate": "2002-01-01",
        "motTests": [],
    }

    return response


def configure_dvsa_settings():
    settings.dvsa_client_id = "test-client"
    settings.dvsa_client_secret = "test-secret"
    settings.dvsa_api_key = "test-api-key"
    settings.dvsa_scope = "test-scope"
    settings.dvsa_token_url = (
        "https://example.com/token"
    )
    settings.dvsa_base_url = (
        "https://example.com"
    )


def test_access_token_is_reused_while_valid():
    configure_dvsa_settings()

    client = DvsaClient()

    with (
        patch(
            "app.services.dvsa_client.httpx.post"
        ) as mock_post,
        patch(
            "app.services.dvsa_client.httpx.get"
        ) as mock_get,
    ):
        mock_post.return_value = token_response(
            "token-one"
        )

        mock_get.return_value = vehicle_response(
            200
        )

        client.get_vehicle_by_registration(
            "LB02BYW"
        )

        client.get_vehicle_by_registration(
            "LB02BYW"
        )

    # Two vehicle checks should only need one authentication request.
    assert mock_post.call_count == 1
    assert mock_get.call_count == 2


def test_expired_token_is_refreshed_before_request():
    configure_dvsa_settings()

    client = DvsaClient()

    with (
        patch(
            "app.services.dvsa_client.httpx.post"
        ) as mock_post,
        patch(
            "app.services.dvsa_client.httpx.get"
        ) as mock_get,
        patch(
            "app.services.dvsa_client.time.time"
        ) as mock_time,
    ):
        mock_time.side_effect = [
            1000,
            1000,
            5000,
            5000,
        ]

        mock_post.side_effect = [
            token_response("old-token"),
            token_response("new-token"),
        ]

        mock_get.return_value = vehicle_response(
            200
        )

        client.get_vehicle_by_registration(
            "LB02BYW"
        )

        client.get_vehicle_by_registration(
            "LB02BYW"
        )

    assert mock_post.call_count == 2


def test_rejected_cached_token_is_refreshed_and_retried():
    configure_dvsa_settings()

    client = DvsaClient()

    with (
        patch(
            "app.services.dvsa_client.httpx.post"
        ) as mock_post,
        patch(
            "app.services.dvsa_client.httpx.get"
        ) as mock_get,
    ):
        mock_post.side_effect = [
            token_response("old-token"),
            token_response("new-token"),
        ]

        mock_get.side_effect = [
            vehicle_response(403),
            vehicle_response(200),
        ]

        vehicle = (
            client.get_vehicle_by_registration(
                "LB02BYW"
            )
        )

    assert mock_post.call_count == 2
    assert mock_get.call_count == 2

    assert vehicle.registration == "LB02BYW"
    assert vehicle.make == "TOYOTA"