from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fireguard.environment import UnavailableProvider


@dataclass
class EnvironmentalObservation:
    """Normalized environmental observation with explicit freshness metadata."""

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "location": self.location,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "rainfall": self.rainfall,
            "pressure": self.pressure,
            "pm25": self.pm25,
            "pm10": self.pm10,
            "visibility": self.visibility,
            "freshness": self.freshness,
            "status": self.status,
            "demo": self.demo,
            "message": self.message,
        }


class EnvironmentalService:
    """Normalize data from real or demo providers while preserving uncertainty metadata."""

    def __init__(self, provider: Any | None = None):
        self.provider = provider or UnavailableProvider()

    async def fetch(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        payload = await self.provider.current(latitude, longitude)
        observation = EnvironmentalObservation(
            timestamp=payload.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source=payload.get("source", "UNAVAILABLE"),
            location={"latitude": latitude, "longitude": longitude} if latitude is not None and longitude is not None else None,
            temperature=payload.get("temperature"),
            humidity=payload.get("humidity"),
            wind_speed=payload.get("wind_speed"),
            wind_direction=payload.get("wind_direction"),
            rainfall=payload.get("rainfall"),
            pressure=payload.get("pressure"),
            pm25=payload.get("pm25"),
            pm10=payload.get("pm10"),
            visibility=payload.get("visibility"),
            freshness=payload.get("freshness", "UNAVAILABLE"),
            status=payload.get("status", "UNAVAILABLE"),
            demo=bool(payload.get("demo", False)),
            message=payload.get("message"),
        )
        return observation.to_dict()
