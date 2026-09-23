from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FIREGUARD_", extra="ignore")

    app_name: str = "ForestGuard"
    model_weights: str = "models/wildfire_yolo.pt"
    device: str = "cpu"
    confidence_threshold: float = 0.35
    frame_interval_seconds: float = 1.0
    upload_max_mb: int = 100
    cors_origins: str = "http://localhost:5173"
    alert_cooldown_seconds: int = 300
    webhook_url: str | None = None
    log_path: str = "data/detections.json"
    dataset_path: str = ""


settings = Settings()
