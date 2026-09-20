from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AlertService:
    alerts: list[dict[str, Any]] = field(default_factory=list)

    def push(self, event_id: str, level: int, title: str, message: str, dedup_key: str | None = None) -> dict[str, Any]:
        dedup = dedup_key or f"{event_id}:{level}:{title}"
        if any(item.get("dedup_key") == dedup for item in self.alerts):
            return {"status": "deduplicated", "dedup_key": dedup}
        alert = {
            "event_id": event_id,
            "level": level,
            "title": title,
            "message": message,
            "dedup_key": dedup,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False,
        }
        self.alerts.append(alert)
        return alert

    def list_alerts(self) -> list[dict[str, Any]]:
        return self.alerts
