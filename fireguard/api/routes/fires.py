from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/fires")
async def list_fires() -> list[dict]:
    return []


@router.get("/fires/{event_id}")
async def get_fire(event_id: str) -> dict:
    return {
        "event_id": event_id,
        "status": "ACTIVE",
        "confidence": 0.92,
        "risk_score": 82.4,
        "growth_rate": 18.3,
        "spread_direction": "NE",
        "location": {"latitude": 14.1234, "longitude": 77.5678},
    }
