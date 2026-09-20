from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fireguard.environment import UnavailableProvider


@dataclass
class EnvironmentalObservation:
    timestamp: str
    source: str = "UNAVAILABLE"
    location: dict[str, float] | None = None
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    rainfall: float | None = None
    pressure: float | None = None
    pm25: float | None = None
    pm10: float | None = None
    visibility: float | None = None
    freshness: str = "UNAVAILABLE"
    status: str = "UNAVAILABLE"
    demo: bool = False
    message: str | None = None
    units: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class EnvironmentalService:
    """Normalize provider responses and classify observation freshness."""

    def __init__(self, provider: Any | None = None, max_age_seconds: int = 300):
        self.provider = provider or UnavailableProvider()
        self.max_age_seconds = max_age_seconds

    def _freshness(self, timestamp: str, current: str) -> str:
        if current in {"UNAVAILABLE", "DEMO_MODE"}:
            return "UNAVAILABLE" if current == "UNAVAILABLE" else "LIVE"
        try:
            observed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds()
            if age <= 60:
                return "LIVE"
            if age <= self.max_age_seconds:
                return "RECENT"
            return "STALE"
        except (TypeError, ValueError):
            return "UNAVAILABLE"

    async def fetch(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        payload = await self.provider.current(latitude, longitude)
        timestamp = payload.get("timestamp", datetime.now(timezone.utc).isoformat())
        status = payload.get("status", "UNAVAILABLE")
        payload["freshness"] = self._freshness(timestamp, status)
        payload["location"] = {"latitude": latitude, "longitude": longitude} if latitude is not None and longitude is not None else None
        return EnvironmentalObservation(
            timestamp=timestamp,
            source=payload.get("source", "UNAVAILABLE"),
            location=payload["location"],
            temperature=payload.get("temperature"), humidity=payload.get("humidity"),
            wind_speed=payload.get("wind_speed"), wind_direction=payload.get("wind_direction"),
            rainfall=payload.get("rainfall"), pressure=payload.get("pressure"),
            pm25=payload.get("pm25"), pm10=payload.get("pm10"), visibility=payload.get("visibility"),
            freshness=payload["freshness"], status=status, demo=bool(payload.get("demo", False)),
            message=payload.get("message"), units=payload.get("units"),
        ).to_dict()
