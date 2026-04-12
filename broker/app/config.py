from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    broker_public_base_url: str = Field(alias="BROKER_PUBLIC_BASE_URL")
    broker_bootstrap_secret: str = Field(alias="BROKER_BOOTSTRAP_SECRET")
    broker_jwt_secret: str = Field(alias="BROKER_JWT_SECRET")
    broker_data_dir: Path = Field(default=Path("/workspace/data"), alias="BROKER_DATA_DIR")
    broker_artifact_dir: Path = Field(default=Path("/workspace/artifacts"), alias="BROKER_ARTIFACT_DIR")
    broker_runtime_host: str = Field(default="127.0.0.1", alias="BROKER_RUNTIME_HOST")
    broker_runtime_port: int = Field(default=9876, alias="BROKER_RUNTIME_PORT")
    broker_viewer_base_url: str | None = Field(default=None, alias="BROKER_VIEWER_BASE_URL")
    broker_token_ttl_seconds: int = Field(default=6 * 60 * 60, alias="BROKER_TOKEN_TTL_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
settings.broker_data_dir.mkdir(parents=True, exist_ok=True)
settings.broker_artifact_dir.mkdir(parents=True, exist_ok=True)
