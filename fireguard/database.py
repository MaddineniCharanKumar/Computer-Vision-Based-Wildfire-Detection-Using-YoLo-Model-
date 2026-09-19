from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import json

from sqlmodel import Session, create_engine, SQLModel, select

from .config import settings

engine = create_engine(settings.database_url, echo=False)


def get_session():
    return Session(engine)


def ensure_database() -> None:
    from .models import create_db_and_tables
    create_db_and_tables(engine)


def seed_demo_data() -> None:
    from .models import CameraSource, EnvironmentalReading, FireEvent
    with get_session() as session:
        if session.exec(select(CameraSource)).first() is None:
            session.add(CameraSource(name="Demo Camera 01", source_type="DEMO", url="demo://camera-01", latitude=37.7749, longitude=-122.4194))
            session.add(EnvironmentalReading(camera_id="demo-01", temperature=32.5, humidity=31.0, wind_speed=24.0, wind_direction=210.0, rainfall=0.0, pressure=1012.0, pm25=18.5, pm10=25.0, visibility=8.5, source="DEMO DATA", timestamp="2026-09-19T00:00:00Z"))
            session.add(FireEvent(event_id="demo-event-001", camera_id="demo-01", source_type="DEMO", status="DETECTED", risk_score=54.0, confidence=0.86, growth_rate=12.0, spread_direction="NORTH", latitude=37.7749, longitude=-122.4194, model_version="demo-v1"))
        session.commit()
