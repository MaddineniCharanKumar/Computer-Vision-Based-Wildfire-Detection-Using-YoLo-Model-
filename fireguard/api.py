from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from fireguard.config import settings
from fireguard.environment import DemoProvider, UnavailableProvider, WeatherAPIProvider
from fireguard.runtime import FireguardRuntime
from utils.device import configure_precision, detect_device, get_gpu_info, get_gpu_memory, get_gpu_utilization

app = FastAPI(title="EcoSpread-YOLO", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = FireguardRuntime(model_path=settings.model_weights, device=settings.device or detect_device())
if settings.demo_mode:
    environment_provider = DemoProvider()
elif settings.environment_provider.lower() == "weather":
    environment_provider = WeatherAPIProvider()
else:
    environment_provider = UnavailableProvider()


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)


manager = ConnectionManager()


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "demo_mode": settings.demo_mode,
        "environment_provider": getattr(environment_provider, "name", "UNAVAILABLE"),
        "model_status": runtime.get_status()["status"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/system/gpu")
async def system_gpu() -> dict[str, Any]:
    gpu = detect_device()
    return {
        "device": gpu,
        "precision": configure_precision(gpu),
        "gpu_info": get_gpu_info(),
        "gpu_memory": get_gpu_memory(),
        "gpu_utilization": get_gpu_utilization(),
    }


@app.get("/api/model/status")
async def model_status() -> dict[str, Any]:
    return runtime.get_status()


@app.post("/api/detection/image")
async def detection_image(file: UploadFile = File(...)) -> dict[str, Any]:
    if not settings.model_weights:
        raise HTTPException(status_code=503, detail="Model weights are not configured. Detection is unavailable.")
    return {
        "status": "accepted",
        "file": file.filename,
        "message": "Inference job accepted. Real model execution is required to produce detections.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/detection/video")
async def detection_video(file: UploadFile = File(...)) -> dict[str, Any]:
    if not settings.model_weights:
        raise HTTPException(status_code=503, detail="Model weights are not configured. Video inference is unavailable.")
    return {
        "status": "accepted",
        "file": file.filename,
        "message": "Video inference job accepted. Real model execution is required to produce detections.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/cameras")
async def cameras() -> list[dict[str, Any]]:
    return []


@app.post("/api/camera/{camera_id}/start")
async def camera_start(camera_id: str) -> dict[str, Any]:
    return {"camera_id": camera_id, "status": "START_REQUESTED", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/camera/{camera_id}/stop")
async def camera_stop(camera_id: str) -> dict[str, Any]:
    return {"camera_id": camera_id, "status": "STOP_REQUESTED", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/fires")
async def fires() -> list[dict[str, Any]]:
    return []


@app.get("/api/fires/{fire_id}")
async def fire_detail(fire_id: str) -> dict[str, Any]:
    raise HTTPException(status_code=404, detail=f"Fire event '{fire_id}' was not found.")


@app.get("/api/environment/current")
async def environment_current(latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
    return await environment_provider.current(latitude, longitude)


@app.get("/api/environment/history")
async def environment_history() -> list[dict[str, Any]]:
    return []


@app.get("/api/risk/{event_id}")
async def risk(event_id: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "score": 0.0,
        "level": "LOW",
        "features": {},
        "status": "UNAVAILABLE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/alerts")
async def alerts() -> list[dict[str, Any]]:
    return []


@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str) -> dict[str, Any]:
    return {"alert_id": alert_id, "status": "ACKNOWLEDGED", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/analytics/overview")
async def analytics_overview() -> dict[str, Any]:
    return {
        "total_events": 0,
        "active_events": 0,
        "alert_count": 0,
        "risk_level": "LOW",
        "source_status": "UNAVAILABLE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
