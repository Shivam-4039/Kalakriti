"""Application settings and environment configuration."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    """Application configuration loaded from Backend/.env."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Kalakriti API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kalakriti"

    # --- Supabase (Auth + Storage) ---
    supabase_url: str = "https://placeholder.supabase.co"
    supabase_service_role_key: SecretStr = SecretStr("placeholder_service_role_key")
    supabase_jwt_secret: str = "placeholder_jwt_secret"
    supabase_storage_bucket: str = "kalakriti-media"
    storage_timeout_seconds: float = Field(default=15.0, gt=0, le=60)

    # --- Sarvam.ai (Primary STT + TTS) ---
    sarvam_api_key: SecretStr = SecretStr("placeholder_sarvam_key")
    sarvam_stt_timeout_seconds: float = Field(default=10.0, gt=0, le=30.0)
    sarvam_tts_timeout_seconds: float = Field(default=10.0, gt=0, le=30.0)

    # --- Groq (LLM for description/translation + Whisper STT fallback) ---
    groq_api_keys: SecretStr = SecretStr("placeholder_groq_key")
    groq_timeout_seconds: float = Field(default=15.0, gt=0, le=30.0)

    # --- CORS ---
    cors_origins: str = "http://localhost:8081,http://127.0.0.1:8081,*"

    # --- Upload limits ---
    max_image_upload_bytes: int = Field(default=3_000_000, gt=0)
    max_audio_upload_bytes: int = Field(default=10_000_000, gt=0)

    # --- Pricing bounds (INR) ---
    pricing_min_inr: int = Field(default=50, ge=1)
    pricing_max_inr: int = Field(default=50_000, ge=50)

    # --- Model paths ---
    pricing_model_path: Path = PROJECT_ROOT / "AI_Model" / "pricing" / "model.pkl"
    craft_gi_mapping_path: Path = (
        PROJECT_ROOT / "AI_Model" / "craft_gi" / "craft_gi_mapping.json"
    )

    # --- ONDC ---
    ondc_mock_mode: bool = True
    ondc_timeout_seconds: float = Field(default=8.0, gt=0, le=30.0)

    # --- Error tracking (optional) ---
    sentry_dsn: str | None = None

    # --- Validators ---

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must start with postgresql+asyncpg:// "
                "for SQLAlchemy async PostgreSQL access."
            )
        return value

    @field_validator("supabase_url")
    @classmethod
    def validate_http_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Value must be a valid http:// or https:// URL.")
        return value.rstrip("/")

    @field_validator("supabase_service_role_key", "sarvam_api_key")
    @classmethod
    def validate_required_secret(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("Required API key cannot be empty.")
        return value

    @field_validator("groq_api_keys")
    @classmethod
    def validate_groq_keys(cls, value: SecretStr) -> SecretStr:
        keys = [key.strip() for key in value.get_secret_value().split(",")]
        keys = [key for key in keys if key]
        if not keys:
            raise ValueError("GROQ_API_KEYS must contain at least one API key.")
        return SecretStr(",".join(keys))

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [origin.strip().rstrip("/") for origin in value.split(",")]
        origins = [origin for origin in origins if origin]
        if not origins:
            raise ValueError("CORS_ORIGINS must contain at least one origin.")
        return ",".join(origins)

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.pricing_min_inr >= self.pricing_max_inr:
            raise ValueError("PRICING_MIN_INR must be less than PRICING_MAX_INR.")

        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be false in production.")
            if "*" in self.cors_origin_list:
                raise ValueError("Wildcard CORS origins not allowed in production.")
            if any(
                "localhost" in o or "127.0.0.1" in o for o in self.cors_origin_list
            ):
                raise ValueError("Localhost CORS origins not allowed in production.")

        return self

    # --- Properties ---

    @property
    def cors_origin_list(self) -> list[str]:
        return self.cors_origins.split(",")

    @property
    def groq_api_key_list(self) -> tuple[str, ...]:
        return tuple(self.groq_api_keys.get_secret_value().split(","))

    @property
    def price_min(self) -> float:
        """Alias for pricing_min_inr as float."""
        return float(self.pricing_min_inr)

    @property
    def price_max(self) -> float:
        """Alias for pricing_max_inr as float."""
        return float(self.pricing_max_inr)


@lru_cache
def get_settings() -> Settings:
    """Create settings once per running API process."""
    return Settings()


# Singleton instance exported for imports across app and alembic
settings = get_settings()