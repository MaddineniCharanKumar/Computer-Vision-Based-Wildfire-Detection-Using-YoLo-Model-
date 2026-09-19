from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DatasetStatistics(BaseModel):
    dataset: str | None = None
    counts: dict[str, int] = Field(default_factory=dict)
    annotation_formats: list[str] = Field(default_factory=list)
    classes: dict[str, int] = Field(default_factory=dict)
    missing_labels: list[str] = Field(default_factory=list)
    orphan_labels: list[str] = Field(default_factory=list)
    corrupted_files: list[dict[str, str]] = Field(default_factory=list)
    invalid_boxes: list[dict[str, Any]] = Field(default_factory=list)
    duplicates: list[dict[str, Any]] = Field(default_factory=list)
    quality: dict[str, Any] = Field(default_factory=dict)


class EnvironmentalSnapshot(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    rainfall: float | None = None
    pressure: float | None = None
    pm25: float | None = None
    pm10: float | None = None
    visibility: float | None = None
    source: str = "DEMO DATA"
    timestamp: str | None = None
    demo: bool = False


class FireEventCreate(BaseModel):
    camera_id: str
    source_type: str = "IMAGE"
    confidence: float = 0.0
    risk_score: float = 0.0
    growth_rate: float = 0.0
    spread_direction: str = "UNKNOWN"
    status: str = "DETECTED"
    model_version: str = "unknown"


class AlertPayload(BaseModel):
    event_id: str
    level: int = 0
    title: str
    message: str
    dedup_key: str | None = None
