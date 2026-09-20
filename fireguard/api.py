from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from fireguard.config import settings
from fireguard.environment import DemoProvider, OpenMeteoProvider, UnavailableProvider
from fireguard.runtime import FireguardRuntime
from fireguard.services import AlertService, DetectionService, EnvironmentalService, ForecastService, GeolocationService, RiskService
from utils.device import configure_precision, detect_device, get_gpu_info, get_gpu_memory, get_gpu_utilization

app = FastAPI(title="EcoSpread-YOLO", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

runtime = FireguardRuntime(model_path=settings.model_weights, device=settings.device or detect_device())
if settings.demo_mode:
    environment_provider = DemoProvider()
elif settings.environment_provider.lower() in {"open_meteo", "open-meteo", "weather", "live"}:
    environment_provider = OpenMeteoProvider(settings.weather_api_url, settings.environment_timeout_seconds)
else:
    environment_provider = UnavailableProvider()

environment_service = EnvironmentalService(environment_provider, settings.environment_max_age_seconds)
alert_service = AlertService()
risk_service = RiskService()
detection_service = DetectionService(model_path=settings.model_weights, device=settings.device, confidence_threshold=settings.confidence_threshold)
forecast_service = ForecastService()


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
        stale = []
        for connection in self.connections:
            try:
                await connection.send_json(payload)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "healthy", "demo_mode": settings.demo_mode, "environment_provider": environment_provider.name, "model_status": runtime.get_status()["status"], "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/system/gpu")
async def system_gpu() -> dict[str, Any]:
    device = detect_device()
    return {"device": device, "precision": configure_precision(device), "gpu_info": get_gpu_info(), "gpu_memory": get_gpu_memory(), "gpu_utilization": get_gpu_utilization()}


@app.get("/api/model/status")
async def model_status() -> dict[str, Any]:
    return runtime.get_status()


@app.post("/api/detection/image")
async def detection_image(file: UploadFile = File(...)) -> dict[str, Any]:
    if not settings.model_weights:
        raise HTTPException(status_code=503, detail="Model weights are not configured. Detection is unavailable.")
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")
    return {"status": "accepted", "file": file.filename, "message": "Inference requires the configured detector worker.", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/environment/current")
async def environment_current(latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
    result = await environment_service.fetch(latitude, longitude)
    await manager.broadcast({"type": "environment_update", "timestamp": datetime.now(timezone.utc).isoformat(), "source": result["source"], "payload": result})
    return result


@app.get("/api/environment/history")
async def environment_history() -> list[dict[str, Any]]:
    return []


@app.get("/api/alerts")
async def alerts() -> list[dict[str, Any]]:
    return alert_service.list_alerts()


@app.get("/api/fires")
async def fires() -> list[dict[str, Any]]:
    return []


@app.get("/api/analytics/overview")
async def analytics_overview() -> dict[str, Any]:
    return {"total_events": 0, "active_events": 0, "alert_count": 0, "risk_level": "LOW", "source_status": environment_provider.name, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
