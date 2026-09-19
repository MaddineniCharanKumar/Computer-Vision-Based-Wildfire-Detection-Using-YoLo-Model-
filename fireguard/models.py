from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlmodel import Field, SQLModel, Relationship, Session, create_engine, select

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str | None = Field(default=None)
    password_hash: str
    is_active: bool = True

class CameraSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    source_type: str
    url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    enabled: bool = True

class FireEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True, unique=True)
    camera_id: str | None = Field(default=None)
    source_type: str | None = Field(default=None)
    status: str = Field(default="DETECTED")
    start_time: str | None = None
    last_seen: str | None = None
    duration: float = 0.0
    risk_score: float = 0.0
    alert_level: int = 0
    confidence: float = 0.0
    growth_rate: float = 0.0
    spread_direction: str = "UNKNOWN"
    latitude: float | None = None
    longitude: float | None = None
    model_version: str | None = None

class Detection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str | None = Field(default=None, index=True)
    camera_id: str | None = Field(default=None)
    confidence: float = 0.0
    bbox: str | None = None
    centroid_x: float | None = None
    centroid_y: float | None = None
    timestamp: str | None = None

class Track(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    track_id: str = Field(index=True)
    camera_id: str | None = None
    bbox: str | None = None
    centroid_x: float | None = None
    centroid_y: float | None = None
    velocity: float = 0.0
    area: float = 0.0
    duration: float = 0.0
    growth_rate: float = 0.0

class EnvironmentalReading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_id: str | None = Field(default=None)
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

class RiskScore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True)
    score: float = 0.0
    level: str = "LOW"
    visual_score: float = 0.0
    persistence: float = 0.0
    growth: float = 0.0
    wind: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    dryness: float = 0.0
    smoke: float = 0.0
    created_at: str | None = None

class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True)
    level: int = 0
    title: str
    message: str
    dedup_key: str | None = Field(default=None, index=True)
    acknowledged: bool = False
    created_at: str | None = None

class ModelVersion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True, unique=True)
    status: str = "trained"
    metrics: str | None = None
    created_at: str | None = None

class InferenceLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_id: str | None = Field(default=None)
    source_type: str | None = Field(default=None)
    fps: float | None = None
    latency_ms: float | None = None
    duration_ms: float | None = None
    model_version: str | None = None
    created_at: str | None = None

class NotificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    alert_id: int | None = Field(default=None)
    provider: str = "webhook"
    status: str = "queued"
    payload: str | None = None
    created_at: str | None = None


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
