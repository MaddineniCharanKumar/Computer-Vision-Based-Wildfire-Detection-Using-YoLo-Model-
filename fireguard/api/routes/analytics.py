from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/analytics/overview")
async def analytics_overview() -> dict:
    return {
        "total_events": 1,
        "active_events": 1,
        "alert_count": 1,
        "risk_level": "HIGH",
        "source_status": "LIVE",
    }
