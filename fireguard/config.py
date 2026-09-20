from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FIREGUARD_", extra="ignore")

    app_name: str = "EcoSpread-YOLO"
    demo_mode: bool = False
    database_url: str = "sqlite:///./fireguard.db"
    model_weights: str | None = None
    device: str = "cpu"
    dataset_path: str = ""
    cors_origins: str = "http://localhost:5173"

    confidence_threshold: float = 0.35
    temporal_window: int = 12
    minimum_persistence: int = 3
    camera_frame_skip: int = 0

    environment_provider: str = "unavailable"
    weather_api_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_api_key: str | None = None
    environment_max_age_seconds: int = 300
    environment_timeout_seconds: float = 10.0

    alert_cooldown_seconds: int = 60
    upload_max_mb: int = 100

    camera_url: str | None = None
    camera_id: str = "default-camera"
    satellite_provider: str = "none"
    terrain_provider: str = "none"
    vegetation_provider: str = "none"

    alert_threshold: float = 0.6
    forecast_horizons: str = "30,60"

settings = Settings()
