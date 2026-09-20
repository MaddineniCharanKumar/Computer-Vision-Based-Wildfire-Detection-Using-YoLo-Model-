from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from fireguard.config import settings
from fireguard.database import ensure_database, get_session
from fireguard.environment import DemoProvider, UnavailableProvider, WeatherAPIProvider
from fireguard.models import Alert, CameraSource, EnvironmentalReading, FireEvent
from fireguard.runtime import FireguardRuntime
from utils.device import configure_precision, detect_device, get_gpu_info, get_gpu_memory, get_gpu_utilization


app = FastAPI(title="FIREGUARD AI", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = FireguardRuntime(model_path=settings.model_weights, device=detect_device())
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

    async def broadcast(self, payload: dict[str, Any]) -> None:
        message = json.dumps(payload, default=str)
        stale: list[WebSocket] = []
        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()


@app.on_event("startup")
def startup() -> None:
    ensure_database()


@app.get("/api/health")
async def health() -> dict[str, Any]:
    database = "healthy"
    try:
        with get_session() as session:
            session.exec(select(CameraSource)).first()
    except Exception as exc:
        database = f"unavailable: {exc.__class__.__name__}"
    status = runtime.get_status()
    return {
        "backend": "healthy",
        "database": database,
        "gpu": "available" if detect_device() == "cuda" else "unavailable",
        "model": "loaded" if status.get("model_path") else "unavailable",
        "camera": "not_configured",
        "environment": getattr(environment_provider, "name", "UNAVAILABLE"),
        "websocket": "ready",
        "demo_mode": settings.demo_mode,
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
        return {"status": "NOT_INSPECTED", "message": "Run the dataset inspector first."}
    return json.loads(report_path.read_text(encoding="utf-8"))


@app.get("/api/model/status")
async def model_status() -> dict[str, Any]:
    return runtime.get_status()


@app.get("/api/environment/current")
async def current_environment(latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
    result = await environment_provider.current(latitude, longitude)
    await manager.broadcast({"type": "environment", "data": result})
    return result


@app.get("/api/fires")
async def fires() -> list[dict[str, Any]]:
    with get_session() as session:
        return [event.model_dump() for event in session.exec(select(FireEvent)).all()]


@app.get("/api/alerts")
async def alerts() -> list[dict[str, Any]]:
    with get_session() as session:
        return [alert.model_dump() for alert in session.exec(select(Alert)).all()]


@app.get("/api/cameras")
async def cameras() -> list[dict[str, Any]]:
    with get_session() as session:
        return [camera.model_dump(exclude={"url"}) for camera in session.exec(select(CameraSource)).all()]


@app.get("/api/analytics/overview")
async def overview() -> dict[str, Any]:
    with get_session() as session:
        events = session.exec(select(FireEvent)).all()
        alerts_list = session.exec(select(Alert)).all()
    active = [event for event in events if event.status != "RESOLVED"]
    return {
        "total_events": len(events),
        "active_events": len(active),
        "alert_count": len(alerts_list),
        "risk_level": max((event.alert_level for event in events), default=0),
        "source_status": "DEMO" if settings.demo_mode else "LIVE/UNAVAILABLE",
    }


@app.post("/api/detection/image")
async def detection_image(file: UploadFile = File(...)) -> dict[str, Any]:
    if not settings.model_weights:
        raise HTTPException(status_code=503, detail="Model weights are unavailable; detection not run.")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        raise HTTPException(status_code=415, detail="Unsupported image extension.")
    contents = await file.read(settings.upload_max_mb * 1024 * 1024 + 1)
    if len(contents) > settings.upload_max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Upload exceeds configured size limit.")
    raise HTTPException(status_code=501, detail="Model inference worker is not configured in this deployment.")


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
