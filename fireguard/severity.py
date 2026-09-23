from __future__ import annotations

from typing import Iterable


def severity(detections: Iterable[dict], width: int = 1, height: int = 1) -> str:
    items = list(detections); fires = [d for d in items if d.get("class") == "fire"]
    if not items: return "none"
    if not fires: return "smoke_only"
    large = any(((d["bbox"][2]-d["bbox"][0]) * (d["bbox"][3]-d["bbox"][1])) / max(width * height, 1) >= .12 and d["confidence"] > .6 for d in fires)
    return "active_wildfire" if large or len(fires) >= 2 else "small_fire"
