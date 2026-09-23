from __future__ import annotations

import asyncio
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fireguard.config import settings
from fireguard.runtime import FireguardRuntime
from fireguard.severity import severity

app = FastAPI(title="ForestGuard Wildfire Intelligence", version="2.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
runtime = FireguardRuntime(settings.model_weights, settings.device)
last_alert = 0.0


def now() -> str: return datetime.now(timezone.utc).isoformat()
def load_history() -> list[dict]:
    path = Path(settings.log_path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
def save_history(item: dict) -> None:
    path = Path(settings.log_path); path.parent.mkdir(parents=True, exist_ok=True)
    records = load_history(); records.insert(0, item); path.write_text(json.dumps(records[:500], indent=2), encoding="utf-8")

async def send_alert(item: dict) -> None:
    global last_alert
    if item["severity"] != "active_wildfire" or not settings.webhook_url or time.time() - last_alert < settings.alert_cooldown_seconds: return
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client: await client.post(settings.webhook_url, json=item)
        last_alert = time.time()
    except Exception: pass

def image_detection(content: bytes, confidence: float):
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(content)).convert("RGB")
        return runtime.predict(image, confidence), image.width, image.height
    except ImportError as exc: raise HTTPException(503, "Install ML dependencies with: pip install -e '.[ml]'") from exc
    except RuntimeError as exc: raise HTTPException(503, str(exc)) from exc
    except Exception as exc: raise HTTPException(400, f"Unable to analyze image: {exc}") from exc

def video_detection(content: bytes, confidence: float, suffix: str) -> list[dict]:
    try:
        import cv2
        with open(Path("/tmp") / f"forestguard-{int(time.time() * 1000)}{suffix}", "wb") as handle: handle.write(content)
        path = Path(handle.name); capture = cv2.VideoCapture(str(path)); fps = capture.get(cv2.CAP_PROP_FPS) or 1.0; step = max(1, int(fps * settings.frame_interval_seconds)); index = 0; frames = []
        while True:
            ok, frame = capture.read()
            if not ok: break
            if index % step == 0:
                detections = runtime.predict(frame, confidence); height, width = frame.shape[:2]
                frames.append({"frame_time": round(index / fps, 3), "detections": detections, "severity": severity(detections, width, height)})
            index += 1
        capture.release(); path.unlink(missing_ok=True); return frames
    except ImportError as exc: raise HTTPException(503, "Install opencv-python with the ML dependencies") from exc
    except RuntimeError as exc: raise HTTPException(503, str(exc)) from exc

@app.get("/api/health")
def health(): return {"status": "healthy", "service": settings.app_name, "model": runtime.get_status(), "timestamp": now()}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), confidenceThreshold: float = .35):
    if not file.filename: raise HTTPException(400, "A filename is required")
    content = await file.read(); suffix = Path(file.filename).suffix.lower(); confidence = max(0.0, min(1.0, confidenceThreshold))
    if suffix in {".mp4", ".mov", ".avi", ".mkv", ".webm"}: frames = video_detection(content, confidence, suffix)
    elif suffix in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        detections, width, height = image_detection(content, confidence); frames = [{"frame_time": 0, "detections": detections, "severity": severity(detections, width, height)}]
    else: raise HTTPException(415, "Unsupported file type")
    all_detections = [detection for frame in frames for detection in frame["detections"]]
    levels = {"none": 0, "smoke_only": 1, "small_fire": 2, "active_wildfire": 3}; overall = max((frame["severity"] for frame in frames), key=lambda level: levels[level], default="none")
    item = {"timestamp": now(), "filename": file.filename, "severity": overall, "top_detection_confidence": max((d["confidence"] for d in all_detections), default=0), "detections": all_detections}
    save_history(item); await send_alert(item)
    return {"status": "completed", "filename": file.filename, "severity": overall, "detections": all_detections, "frames": frames}

@app.get("/api/history")
def history(limit: int = 50): return load_history()[:max(1, min(limit, 500))]
@app.get("/api/model/status")
def model_status(): return runtime.get_status()
