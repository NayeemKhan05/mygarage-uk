from fastapi import HTTPException, status

from app.schemas.dvsa import DvsaVehicle
from app.services.dvsa_client import (
    DvsaAuthenticationError,
    DvsaBadRequestError,
    DvsaClient,
    DvsaConfigurationError,
    DvsaError,
    DvsaRateLimitError,
    DvsaUnavailableError,
    DvsaVehicleNotFoundError,
)


def fetch_dvsa_vehicle(
    dvsa: DvsaClient,
    registration: str,
) -> DvsaVehicle:
    try:
        return dvsa.get_vehicle_by_registration(
            registration
        )

    except DvsaBadRequestError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DVSA rejected this registration",
        )

    except DvsaVehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in DVSA records",
        )

    except DvsaConfigurationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DVSA integration is not configured",
        )

    except DvsaRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DVSA is temporarily rate limiting requests",
        )

    except (
        DvsaAuthenticationError,
        DvsaUnavailableError,
        DvsaError,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve vehicle data from DVSA",
        )