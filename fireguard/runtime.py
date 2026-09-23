from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class FireguardRuntime:
    def __init__(self, model_path: str | None = None, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self._model: Any | None = None

    def get_status(self) -> dict[str, Any]:
        exists = False
        if self.model_path:
            exists = Path(self.model_path).exists()
        return {
            "model_path": self.model_path,
            "device": self.device,
            "status": "READY" if exists else "UNAVAILABLE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Load a YOLO weights file before running predictions.",
        }

    def predict(self, source, confidence: float = 0.35):
        status = self.get_status()
        if status["status"] != "READY":
            raise RuntimeError("Model weights are unavailable. Set FIREGUARD_MODEL_WEIGHTS or place models/wildfire_yolo.pt.")

        if self._model is None:
            from ultralytics import YOLO
            self._model = YOLO(self.model_path)

        results = self._model.predict(source=source, conf=confidence, device=self.device, verbose=False)
        detections: list[dict[str, Any]] = []
        for result in results:
            names = result.names or {}
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            for index, box in enumerate(boxes):
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                xyxy = [float(value) for value in box.xyxy[0].tolist()]
                class_name = names.get(cls_id, str(cls_id))
                detections.append({
                    "class": class_name,
                    "confidence": round(conf, 4),
                    "bbox": [round(v, 2) for v in xyxy],
                    "id": index,
                })
        return detections
