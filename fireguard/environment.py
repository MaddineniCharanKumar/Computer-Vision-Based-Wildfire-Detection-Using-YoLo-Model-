from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EnvironmentalProvider:
    """Provider interface for live environmental measurements."""

    name = "UNAVAILABLE"

    async def current(
        self, latitude: float | None = None, longitude: float | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError


class DemoProvider(EnvironmentalProvider):
    name = "DEMO DATA"

    async def current(
        self, latitude: float | None = None, longitude: float | None = None
    ) -> dict[str, Any]:
        return {
            "temperature": 32.5,
            "humidity": 31.0,
            "wind_speed": 24.0,
            "wind_direction": 210.0,
            "rainfall": 0.0,
            "pressure": 1012.0,
            "pm25": 18.5,
            "pm10": 25.0,
            "visibility": 8.5,
            "source": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo": True,
            "freshness": "LIVE",
            "location_available": latitude is not None and longitude is not None,
        }


class UnavailableProvider(EnvironmentalProvider):
    """Safe default: never invents live measurements."""

    name = "UNAVAILABLE"

    async def current(
        self, latitude: float | None = None, longitude: float | None = None
    ) -> dict[str, Any]:
        return {
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "wind_direction": None,
            "rainfall": None,
            "pressure": None,
            "pm25": None,
            "pm10": None,
            "visibility": None,
            "source": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo": False,
            "freshness": "UNAVAILABLE",
            "message": "No environmental provider is configured.",
            "location_available": latitude is not None and longitude is not None,
        }


class WeatherAPIProvider(UnavailableProvider):
    """Adapter boundary for a real weather service.

    A provider URL and credential must be configured before an HTTP client is
    added. Until then this intentionally returns UNAVAILABLE instead of fake
    weather values.
    """

    name = "WEATHER API UNAVAILABLE"


class SensorProvider(UnavailableProvider):
    name = "SENSOR UNAVAILABLE"


class IoTSensorProvider(UnavailableProvider):
    name = "IOT SENSOR UNAVAILABLE"


class AirQualityProvider(UnavailableProvider):
    name = "AIR QUALITY UNAVAILABLE"


class CSVProvider(EnvironmentalProvider):
    def __init__(self, path: str):
        self.path = Path(path)

    async def current(
        self, latitude: float | None = None, longitude: float | None = None
    ) -> dict[str, Any]:
        if not self.path.exists():
            return await UnavailableProvider().current(latitude, longitude)
        # CSV ingestion belongs in the ingestion worker; do not guess a row or
        # silently treat stale data as current.
        return {
            **await UnavailableProvider().current(latitude, longitude),
            "source": "CSV DATA AVAILABLE - INGESTION REQUIRED",
        }
