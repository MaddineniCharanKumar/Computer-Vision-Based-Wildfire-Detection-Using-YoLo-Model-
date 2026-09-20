from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/alerts")
async def list_alerts() -> list[dict]:
    return []


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str) -> dict:
    return {"alert_id": alert_id, "acknowledged": True}
