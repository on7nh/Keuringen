from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    public_base_url: str = "http://localhost:8080"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "keuringen"
    postgres_user: str = "keuringen_app"
    postgres_password: str = "keuringen_app"

    redis_url: str = "redis://localhost:6379/0"

    document_storage_path: str = "/data/documents"

    ai_gateway_url: str | None = None

    jwt_secret: str = "change-me-in-env-min-32-bytes-long"
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 15
    jwt_refresh_token_days: int = 7

    totp_encryption_key: str = "change-me-32-byte-base64-encoded-key!!"
    totp_issuer: str = "Keuringen"

    webauthn_rp_id: str = "localhost"
    webauthn_rp_name: str = "Digitaal Keurings- en Documentbeheer"
    webauthn_origin: str = "http://localhost:8080"

    step_up_validity_seconds: int = 300
    webauthn_challenge_ttl_seconds: int = 120

    max_upload_size_bytes: int = 100 * 1024 * 1024
    allowed_upload_extensions: tuple[str, ...] = (".pdf", ".jpg", ".jpeg", ".dwg", ".xlsx")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
