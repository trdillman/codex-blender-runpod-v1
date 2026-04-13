from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    broker_public_base_url: str = Field(alias="BROKER_PUBLIC_BASE_URL")
    broker_bootstrap_secret: str = Field(alias="BROKER_BOOTSTRAP_SECRET")
    broker_jwt_secret: str = Field(alias="BROKER_JWT_SECRET")
    broker_data_dir: Path = Field(default=PROJECT_ROOT / ".local" / "data", alias="BROKER_DATA_DIR")
    broker_artifact_dir: Path = Field(default=PROJECT_ROOT / ".local" / "artifacts", alias="BROKER_ARTIFACT_DIR")
    broker_runtime_host: str = Field(default="127.0.0.1", alias="BROKER_RUNTIME_HOST")
    broker_runtime_port: int = Field(default=9876, alias="BROKER_RUNTIME_PORT")
    broker_viewer_base_url: str | None = Field(default=None, alias="BROKER_VIEWER_BASE_URL")
    broker_token_ttl_seconds: int = Field(default=6 * 60 * 60, alias="BROKER_TOKEN_TTL_SECONDS")
    broker_bind_host: str = Field(default="127.0.0.1", alias="BROKER_BIND_HOST")
    broker_bind_port: int = Field(default=8080, alias="BROKER_BIND_PORT")
    broker_sandbox_repo_root: Path = Field(
        default=Path.home() / "Documents" / "Playground" / "blender-edgebox-sandbox",
        alias="BROKER_SANDBOX_REPO_ROOT",
    )
    broker_sandbox_image: str = Field(default="agent-sandbox-blender:local", alias="BROKER_SANDBOX_IMAGE")
    broker_sandbox_owner_id: str = Field(default="codex-local-broker", alias="BROKER_SANDBOX_OWNER_ID")
    broker_sandbox_owner_token: str | None = Field(default=None, alias="BROKER_SANDBOX_OWNER_TOKEN")
    broker_sandbox_gpu: bool = Field(default=False, alias="BROKER_SANDBOX_GPU")
    broker_sandbox_runtime_source: Path = Field(
        default=Path.home() / "Downloads" / "chatgpt-local-mcp-gateway" / "chatgpt-local-mcp-gateway" / "repo_mcp" / "blender_tcp_runtime.py",
        alias="BROKER_SANDBOX_RUNTIME_SOURCE",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
settings.broker_data_dir.mkdir(parents=True, exist_ok=True)
settings.broker_artifact_dir.mkdir(parents=True, exist_ok=True)
