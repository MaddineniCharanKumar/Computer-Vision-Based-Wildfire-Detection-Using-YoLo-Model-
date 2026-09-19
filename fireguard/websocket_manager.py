from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Alert:
    level: int
    title: str
    message: str
    dedup_key: str
    event_id: str | None = None
    acknowledged: bool = False


class AlertEngine:
    """Create alert payloads with deduplication and escalation."""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.cooldown_seconds = 60

    def push(self, event_id: str, level: int, title: str, message: str) -> Alert:
        dedup_key = f"{event_id}:{level}:{title}"
        if any(a.dedup_key == dedup_key for a in self.alerts):
            existing = next(a for a in self.alerts if a.dedup_key == dedup_key)
            existing.acknowledged = False
            return existing

        alert = Alert(level=level, title=title, message=message, dedup_key=dedup_key, event_id=event_id)
        self.alerts.append(alert)
        return alert

    def acknowledge(self, dedup_key: str) -> None:
        for alert in self.alerts:
            if alert.dedup_key == dedup_key:
                alert.acknowledged = True
                return

    def list_recent(self) -> List[Dict[str, Any]]:
        return [
            {"event_id": a.event_id, "level": a.level, "title": a.title, "message": a.message, "dedup_key": a.dedup_key, "acknowledged": a.acknowledged}
            for a in self.alerts
        ]
