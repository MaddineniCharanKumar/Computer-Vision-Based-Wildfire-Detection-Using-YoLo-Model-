from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fireguard.config import settings
from fireguard.environment import DemoProvider, WeatherAPIProvider
from fireguard.runtime import FireguardRuntime
from utils.device import detect_device, get_gpu_info, get_gpu_memory, get_gpu_utilization, configure_precision

app = FastAPI(title="FIREGUARD AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = FireguardRuntime(model_path=settings.model_weights, device=detect_device())
environment_provider = DemoProvider() if settings.demo_mode else WeatherAPIProvider()


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "device": detect_device(),
        "runtime": runtime.get_status(),
    }


@app.get("/api/system/gpu")
async def gpu() -> dict[str, Any]:
    return {
        "device": detect_device(),
        "precision": configure_precision(detect_device()),
        "gpu_info": get_gpu_info(),
        "gpu_memory": get_gpu_memory(),
        "gpu_utilization": get_gpu_utilization(),
    }


@app.get("/api/dataset/statistics")
async def dataset_statistics() -> dict[str, Any]:
    report_path = Path("reports/dataset_report.json")
    if not report_path.exists():
        return {"status": "NOT_INSPECTED", "message": "Run python scripts/inspect_dataset.py --dataset <path> --output reports"}
    return json.loads(report_path.read_text(encoding="utf-8"))


@app.get("/api/model/status")
async def model_status() -> dict[str, Any]:
    return runtime.get_status()


@app.get("/api/environment/current")
async def current_environment() -> dict[str, Any]:
    return await environment_provider.current()


@app.get("/api/fires")
async def fires() -> list[dict[str, Any]]:
    return [{
        "event_id": "demo-event-001",
        "camera_id": "demo-camera-01",
        "status": "DETECTED",
        "confidence": 0.86,
        "risk_score": 54.0,
        "growth_rate": 12.0,
        "spread_direction": "NORTH",
    }]


@app.get("/api/alerts")
async def alerts() -> list[dict[str, Any]]:
    return [{
        "event_id": "demo-event-001",
        "level": 2,
        "title": "Early Warning",
        "message": "Persistent weak detection and growing risk envelope.",
    }]


@app.get("/api/analytics/overview")
async def overview() -> dict[str, Any]:
    return {
        "total_events": 1,
        "active_events": 1,
        "alert_count": 1,
        "risk_level": "HIGH",
        "source_status": "DEMO",
    }


@app.get("/api/analytics/historical")
async def historical() -> dict[str, Any]:
    return {"series": [{"time": "00:00", "risk": 31, "confidence": 0.69}, {"time": "00:10", "risk": 58, "confidence": 0.79}]}
