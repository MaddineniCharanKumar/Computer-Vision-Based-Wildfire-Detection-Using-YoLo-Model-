from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class FireguardRuntime:
    def __init__(self, model_path: str | None = None, device: str = "cpu"):
        self.model_path = model_path
        self.device = device

    def get_status(self) -> dict[str, Any]:
        return {
            "model_path": self.model_path,
            "device": self.device,
            "status": "READY" if self.model_path else "DEMO_MODE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class ModelRuntime:
    def __init__(self, weights_path: str | None = None):
        self.weights_path = weights_path

    def status(self) -> dict[str, Any]:
        return {
            "weights_path": self.weights_path,
            "ready": bool(self.weights_path),
            "note": "Use real YOLO weights before production inference.",
        }


if __name__ == "__main__":
    runtime = FireguardRuntime()
    print(json.dumps(runtime.get_status(), indent=2))
