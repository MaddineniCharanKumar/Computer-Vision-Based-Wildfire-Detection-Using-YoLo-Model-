from __future__ import annotations

import math
from typing import Iterable


def bbox_area(bbox: list[float] | tuple[float, ...]) -> float:
    if len(bbox) < 4:
        return 0.0
    x1, y1, x2, y2 = bbox[:4]
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def severity(detections: Iterable[dict], width: int = 1, height: int = 1) -> str:
    items = list(detections)
    if not items:
        return "none"

    fire_items = [item for item in items if str(item.get("class", "")).lower() == "fire"]
    smoke_items = [item for item in items if str(item.get("class", "")).lower() == "smoke"]

    if not fire_items and not smoke_items:
        return "none"
    if not fire_items:
        return "smoke_only"

    fire_area_ratio = []
    max_conf = 0.0
    for item in fire_items:
        bbox = item.get("bbox") or [0, 0, 0, 0]
        area = bbox_area(bbox)
        image_area = max(1, width * height)
        fire_area_ratio.append(area / image_area)
        max_conf = max(max_conf, float(item.get("confidence", 0.0)))

    large_fire = any(ratio >= 0.12 for ratio in fire_area_ratio) and max_conf > 0.6
    multiple_fire = len(fire_items) >= 2

    if large_fire or multiple_fire:
        return "active_wildfire"
    if any(conf >= 0.35 for conf in [float(item.get("confidence", 0.0)) for item in fire_items]):
        return "small_fire"
    return "smoke_only"
