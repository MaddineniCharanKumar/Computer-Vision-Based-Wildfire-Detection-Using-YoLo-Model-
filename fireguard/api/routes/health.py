from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "demo_mode": False,
        "environment_provider": "UNAVAILABLE",
        "model_status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }
