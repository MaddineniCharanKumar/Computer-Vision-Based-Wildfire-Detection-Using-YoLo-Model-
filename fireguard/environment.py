from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class EnvironmentalProvider:
    """Provider interface for environmental measurements."""

    name = "UNAVAILABLE"

    async def current(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class DataStatus:
    status: str = "UNAVAILABLE"
    freshness: str = "UNAVAILABLE"
    source: str = "UNAVAILABLE"
    demo: bool = False


class UnavailableProvider(EnvironmentalProvider):
    """Safe default that never fabricates live measurements."""

    name = "UNAVAILABLE"

    async def current(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
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
            "status": "UNAVAILABLE",
            "message": "No environmental provider is configured.",
            "location_available": latitude is not None and longitude is not None,
        }


class DemoProvider(EnvironmentalProvider):
    """Explicit demo data source that is clearly labeled and never mixed with live data."""

    name = "DEMO"

    async def current(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
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
            "status": "DEMO_MODE",
            "message": "Demo data is active. This is not live monitoring data.",
            "location_available": latitude is not None and longitude is not None,
        }


class WeatherAPIProvider(UnavailableProvider):
    """Adapter boundary for a real weather service."""

    name = "WEATHER_API"


class SensorProvider(UnavailableProvider):
    name = "SENSOR_PROVIDER"


class IoTSensorProvider(UnavailableProvider):
    name = "IOT_SENSOR_PROVIDER"


class AirQualityProvider(UnavailableProvider):
    name = "AIR_QUALITY_PROVIDER"
