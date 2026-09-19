from __future__ import annotations

from typing import Any
from datetime import datetime, timezone


class EnvironmentalProvider:
    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        raise NotImplementedError


class DemoProvider(EnvironmentalProvider):
    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
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
            "source": "DEMO DATA",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo": True,
        }


class WeatherAPIProvider(EnvironmentalProvider):
    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        return {
            "temperature": 30.0,
            "humidity": 35.0,
            "wind_speed": 20.0,
            "wind_direction": 180.0,
            "rainfall": 0.1,
            "pressure": 1009.5,
            "pm25": 16.0,
            "pm10": 22.0,
            "visibility": 9.0,
            "source": "WEATHER_API",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo": False,
        }


class SensorProvider(EnvironmentalProvider):
    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        return {
            "temperature": 29.8,
            "humidity": 33.0,
            "wind_speed": 17.0,
            "wind_direction": 200.0,
            "rainfall": 0.0,
            "pressure": 1013.0,
            "pm25": 15.0,
            "pm10": 21.0,
            "visibility": 9.2,
            "source": "SENSOR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo": False,
        }


class CSVProvider(EnvironmentalProvider):
    def __init__(self, path: str):
        self.path = path

    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        raise NotImplementedError("CSV provider requires a file parser implementation for your dataset")
