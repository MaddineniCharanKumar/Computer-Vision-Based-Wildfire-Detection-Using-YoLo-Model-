from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class EnvironmentalProvider:
    name = "UNAVAILABLE"

    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        raise NotImplementedError


def _base_payload(latitude: float | None, longitude: float | None) -> dict[str, Any]:
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
        "source": "UNAVAILABLE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo": False,
        "freshness": "UNAVAILABLE",
        "status": "UNAVAILABLE",
        "location_available": latitude is not None and longitude is not None,
    }


class UnavailableProvider(EnvironmentalProvider):
    name = "UNAVAILABLE"

    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        payload = _base_payload(latitude, longitude)
        payload["message"] = "No environmental provider is configured."
        return payload


class DemoProvider(EnvironmentalProvider):
    name = "DEMO"

    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        return {
            "temperature": 32.5, "humidity": 31.0, "wind_speed": 24.0,
            "wind_direction": 210.0, "rainfall": 0.0, "pressure": 1012.0,
            "pm25": 18.5, "pm10": 25.0, "visibility": 8.5,
            "source": self.name, "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo": True, "freshness": "LIVE", "status": "DEMO_MODE",
            "message": "Demo data is active. This is not live monitoring data.",
            "location_available": latitude is not None and longitude is not None,
        }


class OpenMeteoProvider(EnvironmentalProvider):
    """Live weather adapter using Open-Meteo's current weather endpoint.

    Open-Meteo does not require an API key for normal non-commercial usage. The
    provider returns UNAVAILABLE on missing coordinates, timeout, invalid data,
    or upstream failure; it never substitutes values.
    """

    name = "OPEN_METEO"

    def __init__(self, url: str, timeout_seconds: float = 10.0) -> None:
        self.url = url
        self.timeout = httpx.Timeout(timeout_seconds)

    async def current(self, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
        if latitude is None or longitude is None:
            payload = _base_payload(latitude, longitude)
            payload["source"] = self.name
            payload["message"] = "Latitude and longitude are required for live weather data."
            return payload
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join([
                "temperature_2m", "relative_humidity_2m", "precipitation",
                "wind_speed_10m", "wind_direction_10m", "surface_pressure",
            ]),
            "timezone": "UTC",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.url, params=params)
                response.raise_for_status()
                document = response.json()
            current = document.get("current")
            if not isinstance(current, dict):
                raise ValueError("Open-Meteo response did not contain current weather data")
            observed_at = current.get("time")
            if not observed_at:
                raise ValueError("Open-Meteo response did not contain an observation timestamp")
            timestamp = f"{observed_at}:00+00:00" if len(observed_at) == 16 else observed_at
            return {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "rainfall": current.get("precipitation"),
                "pressure": current.get("surface_pressure"),
                "pm25": None, "pm10": None, "visibility": None,
                "source": self.name, "timestamp": timestamp,
                "demo": False, "freshness": "LIVE", "status": "LIVE",
                "location_available": True, "units": document.get("current_units", {}),
            }
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
            logger.warning("Live weather provider failed: %s", exc)
            payload = _base_payload(latitude, longitude)
            payload["source"] = self.name
            payload["message"] = f"Live weather provider unavailable: {exc.__class__.__name__}"
            return payload


class WeatherAPIProvider(OpenMeteoProvider):
    name = "OPEN_METEO"


class SensorProvider(UnavailableProvider):
    name = "SENSOR_PROVIDER"


class CSVProvider(UnavailableProvider):
    name = "CSV_PROVIDER"


class IoTSensorProvider(UnavailableProvider):
    name = "IOT_SENSOR_PROVIDER"


class AirQualityProvider(UnavailableProvider):
    name = "AIR_QUALITY_PROVIDER"


__all__ = ["EnvironmentalProvider", "UnavailableProvider", "DemoProvider", "OpenMeteoProvider", "WeatherAPIProvider", "SensorProvider", "CSVProvider", "IoTSensorProvider", "AirQualityProvider"]
