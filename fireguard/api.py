from __future__ import annotations

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

runtime = FireguardRuntime(settings.model_weights, settings.device)
last_alert_time = 0.0


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_history() -> list[dict]:
    path = Path(settings.log_path)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_history(item: dict) -> None:
    path = Path(settings.log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.insert(0, item)
    path.write_text(json.dumps(history[:500], indent=2), encoding="utf-8")


async def send_alert_if_needed(item: dict) -> None:
    global last_alert_time
    if item.get("severity") != "active_wildfire":
        return
    if not settings.webhook_url:
        return
    if (time.time() - last_alert_time) < settings.alert_cooldown_seconds:
        return

    try:
        import httpx
    except ImportError:
        return

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            await client.post(settings.webhook_url, json=item)
        last_alert_time = time.time()
    except Exception:
        pass


def analyze_image_bytes(content: bytes, confidence: float):
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(content)).convert("RGB")
        detections = runtime.predict(image, confidence)
        return detections, image.width, image.height
    except ImportError as exc:
        raise HTTPException(503, "Install the ML dependencies with: pip install -e '.[ml]'") from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(400, f"Unable to analyze image: {exc}") from exc


def detect_in_video(content: bytes, confidence: float, extension: str):
    try:
        import cv2
    except ImportError as exc:
        raise HTTPException(503, "Install OpenCV with the ML dependencies: pip install -e '.[ml]'") from exc

    temp_path = Path("/tmp") / f"forestguard_{int(time.time() * 1000)}{extension}"
    temp_path.write_bytes(content)

    capture = cv2.VideoCapture(str(temp_path))
    if not capture.isOpened():
        temp_path.unlink(missing_ok=True)
        raise HTTPException(400, "Could not open uploaded video file.")

    fps = capture.get(cv2.CAP_PROP_FPS) or 1.0
    step = max(1, int(round(fps * settings.frame_interval_seconds)))
    frames: list[dict] = []
    frame_index = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_index % step == 0:
            detections = runtime.predict(frame, confidence)
            height, width = frame.shape[:2]
            frames.append({
                "frame_time": round(frame_index / max(fps, 1.0), 3),
                "detections": detections,
                "severity": severity(detections, width, height),
            })
        frame_index += 1

    capture.release()
    temp_path.unlink(missing_ok=True)
    return frames


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": settings.app_name, "model": runtime.get_status(), "timestamp": now()}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), confidenceThreshold: float = 0.35):
    if not file.filename:
        raise HTTPException(400, "A filename is required.")

    confidence = max(0.0, min(1.0, float(confidenceThreshold)))
    content = await file.read()
    suffix = Path(file.filename).suffix.lower()

    if suffix in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
        frames = detect_in_video(content, confidence, suffix)
        all_dets = [d for frame in frames for d in frame["detections"]]
        level_order = {"none": 0, "smoke_only": 1, "small_fire": 2, "active_wildfire": 3}
        overall = max((frame["severity"] for frame in frames), key=lambda level: level_order.get(level, 0), default="none")
        item = {
            "timestamp": now(),
            "filename": file.filename,
            "severity": overall,
            "top_detection_confidence": max((d["confidence"] for d in all_dets), default=0),
            "detections": all_dets,
        }
        save_history(item)
        await send_alert_if_needed(item)
        return {"status": "completed", "filename": file.filename, "severity": overall, "detections": all_dets, "frames": frames}

    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        detections, width, height = analyze_image_bytes(content, confidence)
        severity_level = severity(detections, width, height)
        item = {
            "timestamp": now(),
            "filename": file.filename,
            "severity": severity_level,
            "top_detection_confidence": max((d["confidence"] for d in detections), default=0),
            "detections": detections,
        }
        save_history(item)
        await send_alert_if_needed(item)
        return {
            "status": "completed",
            "filename": file.filename,
            "severity": severity_level,
            "detections": detections,
            "frames": [{"frame_time": 0, "detections": detections, "severity": severity_level}],
        }

    raise HTTPException(415, "Unsupported file type. Use an image or video file.")


@app.get("/api/history")
def history(limit: int = 50):
    records = load_history()
    return records[: max(1, min(limit, 500))]


@app.get("/api/model/status")
def model_status():
    return runtime.get_status()
