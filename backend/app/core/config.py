from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROOT_ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    database_url: str

    dvsa_client_id: str | None = None
    dvsa_client_secret: str | None = None
    dvsa_api_key: str | None = None
    dvsa_scope: str | None = None
    dvsa_token_url: str | None = None
    dvsa_base_url: str = "https://history.mot.api.gov.uk"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    auth_token_expire_minutes: int = 1440
    auth_cookie_name: str = "mygarage_access_token"
    auth_cookie_secure: bool = False

    # Receipt files stay on local disk during development.
    # We'll move this storage behind S3 when MyGarage is deployed.
    upload_dir: Path = PROJECT_ROOT / "uploads"
    max_receipt_size_mb: int = 10

    @property
    def max_receipt_size_bytes(self) -> int:
        return self.max_receipt_size_mb * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()