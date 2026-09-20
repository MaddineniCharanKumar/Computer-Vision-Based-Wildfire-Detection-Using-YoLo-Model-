from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from fireguard.config import settings
from fireguard.environment import DemoProvider, UnavailableProvider, WeatherAPIProvider
from fireguard.runtime import FireguardRuntime
from fireguard.services import AlertService, DetectionService, EnvironmentalService, ForecastService, GeolocationService, RiskService
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

environment_service = EnvironmentalService(environment_provider)
alert_service = AlertService()
risk_service = RiskService()
detection_service = DetectionService(model_path=settings.model_weights, device=settings.device)
forecast_service = ForecastService()
location_service = GeolocationService()


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
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")
    return {
        "status": "accepted",
        "file": file.filename,
        "message": "Inference job accepted. Real model execution is still required to produce detections.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/environment/current")
async def environment_current(latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
    return await environment_service.fetch(latitude, longitude)


@app.get("/api/risk/{event_id}")
async def risk(event_id: str) -> dict[str, Any]:
    features = {
        "visual": 72.0,
        "persistence": 68.0,
        "growth": 58.0,
        "wind": 43.0,
        "temperature": 60.0,
        "humidity": 54.0,
        "dryness": 63.0,
        "smoke": 70.0,
    }
    return {"event_id": event_id, **risk_service.compute(features)}


@app.get("/api/forecast/{event_id}")
async def forecast(event_id: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        **forecast_service.predict(wind_speed=18.0, wind_direction=220.0, humidity=35.0, temperature=32.0, slope=12.0, fuel_load=0.7, horizon_minutes=30),
    }


@app.get("/api/alerts")
async def alerts() -> list[dict[str, Any]]:
    return alert_service.list_alerts()


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
