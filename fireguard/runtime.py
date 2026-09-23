from __future__ import annotations

from pathlib import Path
from typing import Any


class FireguardRuntime:
    def __init__(self, model_path: str | None = None, device: str = "cpu"):
        self.model_path, self.device = model_path, device
        self._model: Any = None

    def get_status(self):
        path = Path(self.model_path) if self.model_path else None
        return {"model_path": self.model_path, "device": self.device, "status": "READY" if path and path.exists() else "UNAVAILABLE", "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}

    def predict(self, source, confidence=.35):
        if self.get_status()["status"] != "READY": raise RuntimeError("Model weights are unavailable. Set FIREGUARD_MODEL_WEIGHTS.")
        if self._model is None:
            from ultralytics import YOLO
            self._model = YOLO(self.model_path)
        results = self._model.predict(source=source, conf=confidence, device=self.device, verbose=False)
        output = []
        for result in results:
            names = result.names or {}
            if result.boxes is None: continue
            for box in result.boxes:
                xyxy = [round(float(v), 2) for v in box.xyxy[0].tolist()]
                output.append({"class": names.get(int(box.cls.item()), str(int(box.cls.item()))), "confidence": round(float(box.conf.item()), 4), "bbox": xyxy})
        return output
