from __future__ import annotations

import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fireguard.config import settings
from fireguard.runtime import FireguardRuntime
from fireguard.severity import severity

app = FastAPI(title="ForestGuard Wildfire Intelligence", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
runtime = FireguardRuntime(settings.model_weights, settings.device)
last_alert = 0.0

def stamp(): return datetime.now(timezone.utc).isoformat()
def history():
    path = Path(settings.log_path)
    return json.loads(path.read_text()) if path.exists() else []
def record(item):
    path = Path(settings.log_path); path.parent.mkdir(parents=True, exist_ok=True); data = history(); data.insert(0, item); path.write_text(json.dumps(data[:500], indent=2))

def analyze_image(content: bytes, confidence: float):
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(content)).convert("RGB")
        detections = runtime.predict(image, confidence)
        return detections, image.width, image.height
    except ImportError as exc: raise HTTPException(503, "Install the ML dependencies with pip install -e '.[ml]'") from exc
    except RuntimeError as exc: raise HTTPException(503, str(exc)) from exc
    except Exception as exc: raise HTTPException(400, f"Unable to analyze image: {exc}") from exc

@app.get("/api/health")
def health(): return {"status": "healthy", "service": settings.app_name, "model": runtime.get_status(), "timestamp": stamp()}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), confidenceThreshold: float = .35):
    if not file.filename: raise HTTPException(400, "A filename is required")
    content = await file.read(); suffix = Path(file.filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}: raise HTTPException(415, "This endpoint currently accepts images. Use /api/analyze/video for video files.")
    detections, width, height = analyze_image(content, max(0.0, min(1.0, confidenceThreshold)))
    level = severity(detections, width, height); item = {"timestamp": stamp(), "filename": file.filename, "severity": level, "top_detection_confidence": max((d["confidence"] for d in detections), default=0), "detections": detections}
    record(item); return {"status": "completed", "filename": file.filename, "severity": level, "detections": detections, "frames": [{"frame_time": 0, "detections": detections, "severity": level}]}

@app.get("/api/history")
def get_history(limit: int = 50): return history()[:max(1, min(limit, 500))]

@app.get("/api/model/status")
def model_status(): return runtime.get_status()
