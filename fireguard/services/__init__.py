from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .environment import DemoProvider, CSVProvider, WeatherAPIProvider, SensorProvider
from .risk import calculate_risk, risk_level
from .analytics import build_overview, build_historical
from .alerts import AlertService
from .tracking import tracker
from .notifications import send_all_notifications
from .database import ensure_database, seed_demo_data
from utils.device import get_gpu_info, get_gpu_memory, get_gpu_utilization, detect_device, configure_precision

app = FastAPI(title="FIREGUARD AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

environment_provider = DemoProvider() if settings.demo_mode else WeatherAPIProvider()
alert_service = AlertService()


@app.on_event("startup")
def startup_event():
    ensure_database()
    seed_demo_data()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "device": detect_device(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/system/gpu")
async def system_gpu():
    return {
        "device": detect_device(),
        "precision": configure_precision(detect_device()),
        "gpu_info": get_gpu_info(),
        "gpu_memory": get_gpu_memory(),
        "gpu_utilization": get_gpu_utilization(),
    }


@app.get("/api/dataset/statistics")
async def dataset_statistics():
    report_path = "reports/dataset_report.json"
    if not os.path.exists(report_path):
        return {"status": "NOT_RUN", "message": "Dataset inspection has not been executed yet. Run: python scripts/inspect_dataset.py --dataset <path> --output reports"}
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/model/status")
async def model_status():
    return {
        "weights_configured": bool(settings.model_weights),
        "model_version": "demo-v1",
        "status": "READY" if settings.model_weights else "DEMO_MODE",
        "metrics_available": False,
    }


@app.post("/api/detection/image")
async def detection_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required")
    return {
        "status": "queued",
        "filename": file.filename,
        "source_type": "IMAGE",
        "demo_mode": settings.demo_mode,
        "message": "Image submission accepted. Real inference should be wired to YOLO and GPU service.",
    }


@app.post("/api/camera/start")
async def camera_start(payload: dict | None = None):
    return {
        "status": "started",
        "camera": payload.get("camera_id", "demo-camera-01") if payload else "demo-camera-01",
        "source_type": "DEMO",
    }


@app.post("/api/camera/stop")
async def camera_stop(payload: dict | None = None):
    return {
        "status": "stopped",
        "camera": payload.get("camera_id", "demo-camera-01") if payload else "demo-camera-01",
    }


@app.get("/api/fires")
async def fires():
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
async def alerts():
    return alert_service.list_alerts()


@app.get("/api/environment/current")
async def environment_current():
    current = await environment_provider.current()
    return current


@app.get("/api/environment/history")
async def environment_history():
    return [{
        "temperature": 32.5,
        "humidity": 31.0,
        "wind_speed": 24.0,
        "source": "DEMO DATA",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }]


@app.get("/api/risk/{event_id}")
async def risk(event_id: str):
    features = {
        "visual": 84.0,
        "persistence": 74.0,
        "growth": 68.0,
        "wind": 58.0,
        "temperature": 67.0,
        "humidity": 58.0,
        "dryness": 62.0,
        "smoke": 80.0,
    }
    result = calculate_risk(features)
    return {"event_id": event_id, **result}


@app.get("/api/analytics/overview")
async def analytics_overview():
    return build_overview()


@app.get("/api/analytics/historical")
async def analytics_historical():
    return build_historical()


@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json({
                "type": "live",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detections": [{"id": "demo-001", "confidence": 0.87, "center": [0.5, 0.45]}],
                "events": [{"event_id": "demo-event-001", "status": "DETECTED", "risk_score": 54.0}],
                "alerts": alert_service.list_alerts(),
                "gpu": get_gpu_info(),
                "fps": 18.4,
            })
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
