"""DVSA MOT History API integration will live here.

Keeping external integrations behind a service layer means route handlers and
business logic do not become coupled to DVSA-specific HTTP details.
"""


import time
from functools import lru_cache

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.dvsa import DvsaVehicle


class DvsaError(Exception):
    pass


class DvsaConfigurationError(DvsaError):
    pass


class DvsaAuthenticationError(DvsaError):
    pass


class DvsaVehicleNotFoundError(DvsaError):
    pass


class DvsaBadRequestError(DvsaError):
    pass


class DvsaRateLimitError(DvsaError):
    pass


class DvsaUnavailableError(DvsaError):
    pass


class DvsaClient:
    def __init__(self):
        self._access_token: str | None = None
        self._token_expires_at = 0.0

    def _check_configuration(self) -> None:
        required_settings = {
            "DVSA_CLIENT_ID": settings.dvsa_client_id,
            "DVSA_CLIENT_SECRET": settings.dvsa_client_secret,
            "DVSA_API_KEY": settings.dvsa_api_key,
            "DVSA_SCOPE": settings.dvsa_scope,
            "DVSA_TOKEN_URL": settings.dvsa_token_url,
        }

        missing = [
            name
            for name, value in required_settings.items()
            if not value
        ]

        if missing:
            raise DvsaConfigurationError(
                f"Missing DVSA configuration: {', '.join(missing)}"
            )

    def _get_access_token(self) -> str:
        self._check_configuration()

        # Reuse the current token until it is close to expiring.
        if (
            self._access_token
            and time.monotonic() < self._token_expires_at
        ):
            return self._access_token

        try:
            response = httpx.post(
                settings.dvsa_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.dvsa_client_id,
                    "client_secret": settings.dvsa_client_secret,
                    "scope": settings.dvsa_scope,
                },
                headers={
                    "Content-Type":
                        "application/x-www-form-urlencoded",
                },
                timeout=10.0,
            )
        except httpx.RequestError as exc:
            raise DvsaUnavailableError(
                "Could not reach the DVSA authentication service"
            ) from exc

        if response.status_code >= 400:
            raise DvsaAuthenticationError(
                "DVSA authentication failed"
            )

        try:
            token_data = response.json()

            access_token = token_data["access_token"]
            expires_in = int(token_data["expires_in"])

        except (KeyError, TypeError, ValueError) as exc:
            raise DvsaAuthenticationError(
                "DVSA returned an invalid authentication response"
            ) from exc

        self._access_token = access_token

        # Refresh slightly early rather than risk using an expired token.
        self._token_expires_at = (
            time.monotonic() + max(expires_in - 30, 0)
        )

        return access_token

    def get_vehicle_by_registration(
        self,
        registration: str,
    ) -> DvsaVehicle:
        access_token = self._get_access_token()

        url = (
            f"{settings.dvsa_base_url}"
            f"/v1/trade/vehicles/registration/{registration}"
        )

        try:
            response = httpx.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-API-Key": settings.dvsa_api_key,
                    "Accept": "application/json",
                },
                timeout=15.0,
            )
        except httpx.RequestError as exc:
            raise DvsaUnavailableError(
                "Could not reach the DVSA MOT History API"
            ) from exc

        if response.status_code == 400:
            raise DvsaBadRequestError(
                "DVSA rejected the registration"
            )

        if response.status_code == 404:
            raise DvsaVehicleNotFoundError(
                "Vehicle not found"
            )

        if response.status_code in (401, 403):
            raise DvsaAuthenticationError(
                "DVSA authentication failed"
            )

        if response.status_code == 429:
            raise DvsaRateLimitError(
                "DVSA rate limit reached"
            )

        if response.status_code >= 500:
            raise DvsaUnavailableError(
                "DVSA is currently unavailable"
            )

        if response.status_code >= 400:
            raise DvsaError(
                "DVSA returned an unexpected error"
            )

        try:
            return DvsaVehicle.model_validate(
                response.json()
            )

        except (ValueError, ValidationError) as exc:
            raise DvsaError(
                "DVSA returned vehicle data we could not understand"
            ) from exc


@lru_cache
def get_dvsa_client() -> DvsaClient:
    return DvsaClient()