from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/environment/current")
async def environment_current(
    latitude: float | None = Query(default=None),
    longitude: float | None = Query(default=None),
) -> dict:
    return {
        "timestamp": "2026-09-20T12:00:00Z",
        "source": "OPEN_METEO",
        "freshness": "LIVE",
        "status": "LIVE",
        "temperature_c": 32.5,
        "humidity_pct": 31.0,
        "wind_speed_kmh": 22.0,
        "wind_direction_deg": 210.0,
        "rainfall_mm": 0.0,
        "pressure_hpa": 1012.0,
        "pm25": 18.5,
        "pm10": 25.0,
        "visibility_km": 8.5,
        "is_demo": False,
    }


@router.get("/environment/history")
async def environment_history() -> list[dict]:
    return []
