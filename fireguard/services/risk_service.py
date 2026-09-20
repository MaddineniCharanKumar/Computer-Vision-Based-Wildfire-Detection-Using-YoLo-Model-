from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DetectionService:
    model_path: str | None = None
    device: str = "cpu"
    confidence_threshold: float = 0.35

    def infer_image(self, image_path: str) -> dict[str, Any]:
        if not self.model_path:
            raise RuntimeError("Model weights are not configured. Real inference is unavailable.")
        return {
            "status": "accepted",
            "source": image_path,
            "detections": [],
            "confidence_threshold": self.confidence_threshold,
            "device": self.device,
        }

    def infer_video(self, video_path: str) -> dict[str, Any]:
        if not self.model_path:
            raise RuntimeError("Model weights are not configured. Real video inference is unavailable.")
        return {
            "status": "accepted",
            "source": video_path,
            "detections": [],
            "device": self.device,
        }
