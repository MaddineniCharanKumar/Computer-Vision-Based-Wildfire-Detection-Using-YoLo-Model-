from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RiskService:
    weights: dict[str, float] = field(default_factory=lambda: {
        "visual": 0.25,
        "persistence": 0.15,
        "growth": 0.15,
        "wind": 0.10,
        "temperature": 0.10,
        "humidity": 0.10,
        "dryness": 0.10,
        "smoke": 0.05,
    })

    def compute(self, features: dict[str, Any]) -> dict[str, Any]:
        score = 0.0
        for key, weight in self.weights.items():
            value = float(features.get(key, 0.0))
            score += min(max(value, 0.0), 100.0) * weight
        score = min(100.0, max(0.0, score))
        result = {
            "score": round(score, 2),
            "level": self.level(score),
            "features": features,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return result

    @staticmethod
    def level(score: float) -> str:
        if score < 20:
            return "LOW"
        if score < 40:
            return "GUARDED"
        if score < 60:
            return "MODERATE"
        if score < 80:
            return "HIGH"
        return "CRITICAL"
