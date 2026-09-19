from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DetectionService:
    model_path: str | None = None
    device: str = "cpu"
    confidence_threshold: float = 0.35

    def infer_image(self, image_path: str) -> dict[str, Any]:
        return {
            "status": "demo",
            "source": image_path,
            "detections": [],
            "confidence_threshold": self.confidence_threshold,
            "note": "Real inference requires a YOLO model and a valid runtime environment.",
        }

    def infer_video(self, video_path: str) -> dict[str, Any]:
        return {
            "status": "demo",
            "source": video_path,
            "detections": [],
            "note": "Real video inference should be attached to the YOLO pipeline.",
        }
