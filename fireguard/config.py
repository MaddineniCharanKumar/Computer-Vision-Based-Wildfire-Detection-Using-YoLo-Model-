from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FIREGUARD_", extra="ignore")

    demo_mode: bool = False
    database_url: str = "sqlite:///./fireguard.db"
    model_weights: str | None = None
    dataset_path: str = r"C:\Users\dines\Downloads\FASDD_UAV"
    cors_origins: str = "http://localhost:5173"
    confidence_threshold: float = 0.35
    temporal_window: int = 12
    minimum_persistence: int = 3


settings = Settings()
