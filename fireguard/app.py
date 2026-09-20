from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fireguard.api.routes import alerts, analytics, detection, environment, fires, health, websocket
from fireguard.config import settings
from fireguard.database import init_db

app = FastAPI(title="EcoSpread-YOLO", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(detection.router, prefix="/api", tags=["detection"])
app.include_router(environment.router, prefix="/api", tags=["environment"])
app.include_router(fires.router, prefix="/api", tags=["fires"])
app.include_router(alerts.router, prefix="/api", tags=["alerts"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])
