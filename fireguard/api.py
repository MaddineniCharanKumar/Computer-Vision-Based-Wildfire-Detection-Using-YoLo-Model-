from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .environment import DemoProvider, WeatherAPIProvider
from .risk import calculate_risk
from utils.device import detect_device, get_gpu_info, get_gpu_memory, get_gpu_utilization, configure_precision

app = FastAPI(title="FIREGUARD AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

environment_provider = DemoProvider() if settings.demo_mode else WeatherAPIProvider()


class CameraStartRequest(BaseModel):
    camera_id: str
    source_type: str = "DEMO"


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device": detect_device(),
    }


@app.get("/api/system/gpu")
async def system_gpu() -> dict[str, Any]:
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
    return {
        "weights_configured": bool(settings.model_weights),
        "status": "READY" if settings.model_weights else "DEMO_MODE",
        "metrics_available": False,
        "model_version": "demo-v1",
    }


@app.post("/api/detection/image")
async def detection_image(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename is required")
    return {
        "status": "queued",
        "filename": file.filename,
        "source_type": "IMAGE",
        "demo_mode": settings.demo_mode,
        "message": "Uploaded image accepted; attach a model for live inference.",
    }


@app.post("/api/camera/start")
async def camera_start(payload: CameraStartRequest) -> dict[str, Any]:
    return {"status": "started", "camera_id": payload.camera_id, "source_type": payload.source_type}


@app.post("/api/camera/stop")
async def camera_stop(payload: CameraStartRequest) -> dict[str, Any]:
    return {"status": "stopped", "camera_id": payload.camera_id, "source_type": payload.source_type}


@app.get("/api/fires")
async def fires() -> list[dict[str, Any]]:
    return [{
        "event_id": "demo-event-001",
        "camera_id": "demo-camera-01",
        "source_type": "DEMO",
        "status": "DETECTED",
        "confidence": 0.86,
        "risk_score": 54.0,
        "growth_rate": 12.0,
        "spread_direction": "NORTH",
        "model_version": "demo-v1",
    }]


@app.get("/api/alerts")
async def alerts() -> list[dict[str, Any]]:
    return [{
        "event_id": "demo-event-001",
        "level": 2,
        "title": "Early Warning",
        "message": "Persistent weak detection. Growth is increasing.",
        "acknowledged": False,
    }]


@app.get("/api/environment/current")
async def environment_current() -> dict[str, Any]:
    return await environment_provider.current()


@app.get("/api/environment/history")
async def environment_history() -> list[dict[str, Any]]:
    return [{
        "temperature": 32.5,
        "humidity": 31.0,
        "wind_speed": 24.0,
        "source": "DEMO DATA",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }]


@app.get("/api/risk/{event_id}")
async def risk(event_id: str) -> dict[str, Any]:
    features = {
        "visual": 82.0,
        "persistence": 70.0,
        "growth": 60.0,
        "wind": 55.0,
        "temperature": 62.0,
        "humidity": 51.0,
        "dryness": 58.0,
        "smoke": 77.0,
    }
    result = calculate_risk(features)
    result["event_id"] = event_id
    return result


@app.get("/api/analytics/overview")
async def analytics_overview() -> dict[str, Any]:
    return {
        "total_events": 1,
        "active_events": 1,
        "alerts": 2,
        "risk_level": "HIGH",
        "gpu_status": "READY",
        "source_status": "DEMO",
    }


@app.get("/api/analytics/historical")
async def analytics_historical() -> dict[str, Any]:
    return {
        "series": [
            {"time": "00:00", "risk": 30, "confidence": 0.62},
            {"time": "00:05", "risk": 46, "confidence": 0.70},
            {"time": "00:10", "risk": 58, "confidence": 0.77},
            {"time": "00:15", "risk": 72, "confidence": 0.83},
        ]
    }


@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json({
                "type": "live",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detections": [{"id": "demo-001", "confidence": 0.87, "center": [0.52, 0.46]}],
                "events": [{"event_id": "demo-event-001", "status": "DETECTED", "risk_score": 54.0}],
                "alerts": [{"level": 2, "title": "Early Warning", "message": "Increasing spread risk"}],
                "gpu": get_gpu_info(),
                "fps": 18.4,
            })
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
