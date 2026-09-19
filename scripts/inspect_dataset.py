from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
LABEL_EXTENSIONS = {".txt", ".xml", ".json"}


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def is_label(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in LABEL_EXTENSIONS


def detect_annotation_format(paths: list[Path]) -> list[str]:
    formats: list[str] = []
    suffixes = {p.suffix.lower() for p in paths}
    if ".txt" in suffixes:
        formats.append("YOLO")
    if ".xml" in suffixes:
        formats.append("VOC/XML")
    if ".json" in suffixes:
        formats.append("COCO/JSON")
    if not formats:
        formats.append("UNKNOWN")
    return formats


def parse_yolo_label(path: Path) -> list[dict[str, Any]]:
    boxes: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) != 5:
            raise ValueError(f"{path}: line {line_number} does not have 5 YOLO fields")
        class_id, x_center, y_center, width, height = [float(part) if idx else int(part) for idx, part in enumerate(parts)]
        boxes.append({
            "class_id": class_id,
            "x_center": x_center,
            "y_center": y_center,
            "width": width,
            "height": height,
        })
    return boxes


def box_is_valid(box: dict[str, Any]) -> bool:
    x_center = float(box["x_center"])
    y_center = float(box["y_center"])
    width = float(box["width"])
    height = float(box["height"])
    if width <= 0 or height <= 0:
        return False
    if not (0.0 <= x_center <= 1.0 and 0.0 <= y_center <= 1.0):
        return False
    if not (0.0 < width <= 1.0 and 0.0 < height <= 1.0):
        return False
    x_min = x_center - (width / 2.0)
    x_max = x_center + (width / 2.0)
    y_min = y_center - (height / 2.0)
    y_max = y_center + (height / 2.0)
    return 0.0 <= x_min and x_max <= 1.0 and 0.0 <= y_min and y_max <= 1.0


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_dataset(dataset_root: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    images = sorted(p for p in dataset_root.rglob("*") if is_image(p))
    labels = sorted(p for p in dataset_root.rglob("*") if is_label(p))
    image_stems = {p.stem for p in images}
    missing_labels: list[str] = []
    orphan_labels: list[str] = []
    invalid_boxes: list[dict[str, Any]] = []
    corrupted_files: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    class_counts: Counter[int] = Counter()
    label_classes: set[int] = set()
    sha_map: dict[str, str] = {}

    for image in images:
        try:
            with Image.open(image) as img:
                img.verify()
        except Exception as exc:
            corrupted_files.append({"file": str(image.relative_to(dataset_root)), "error": str(exc)})
        if not any((image.with_suffix(".txt")).exists(), (image.with_suffix(".xml")).exists(), (image.with_suffix(".json")).exists()):
            missing_labels.append(str(image.relative_to(dataset_root)))

    for label in labels:
        relative = str(label.relative_to(dataset_root))
        stem = label.stem
        if label.suffix.lower() == ".txt":
            if stem not in image_stems:
                orphan_labels.append(relative)
            try:
                boxes = parse_yolo_label(label)
                for box in boxes:
                    class_id = int(box["class_id"])
                    label_classes.add(class_id)
                    class_counts[class_id] += 1
                    if not box_is_valid(box):
                        invalid_boxes.append({"file": relative, "box": box})
            except Exception as exc:
                corrupted_files.append({"file": relative, "error": str(exc)})

    for path in images + labels:
        digest = compute_sha256(path)
        if digest in sha_map:
            duplicates.append({"file": str(path.relative_to(dataset_root)), "same_as": sha_map[digest]})
        else:
            sha_map[digest] = str(path.relative_to(dataset_root))

    quality_issues = []
    if missing_labels:
        quality_issues.append({"issue": "missing_labels", "count": len(missing_labels)})
    if orphan_labels:
        quality_issues.append({"issue": "orphan_labels", "count": len(orphan_labels)})
    if corrupted_files:
        quality_issues.append({"issue": "corrupted_files", "count": len(corrupted_files)})
    if invalid_boxes:
        quality_issues.append({"issue": "invalid_boxes", "count": len(invalid_boxes)})
    if duplicates:
        quality_issues.append({"issue": "duplicates", "count": len(duplicates)})

    quality_status = "PASS" if not quality_issues else "WARN"
    report = {
        "dataset": str(dataset_root),
        "inspected_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "images": len(images),
            "annotations": len(labels),
            "classes_detected": len(class_counts),
            "label_files": len(labels),
            "xml_files": len([p for p in labels if p.suffix.lower() == ".xml"]),
            "json_files": len([p for p in labels if p.suffix.lower() == ".json"]),
        },
        "annotation_formats": detect_annotation_format(labels),
        "classes": {str(key): value for key, value in sorted(class_counts.items())},
        "missing_labels": missing_labels,
        "orphan_labels": orphan_labels,
        "corrupted_files": corrupted_files,
        "invalid_boxes": invalid_boxes,
        "duplicates": duplicates,
        "quality": {
            "status": quality_status,
            "issues": quality_issues,
            "issue_count": sum(item["count"] for item in quality_issues),
        },
    }
    return report


def build_html_report(report: dict[str, Any]) -> str:
    safe = json.dumps(report, indent=2)
    rows = "".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["counts"].items()
    )
    return f"""
    <html>
      <head><meta charset="utf-8"><title>FIREGUARD Dataset Report</title></head>
      <body style="font-family:Arial,sans-serif;padding:24px;">
        <h1>FIREGUARD Dataset Report</h1>
        <p><strong>Status:</strong> {report['quality']['status']}</p>
        <table border="1" cellpadding="6" cellspacing="0">
          <thead><tr><th>Metric</th><th>Value</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        <pre style="white-space:pre-wrap;">{html.escape(safe)}</pre>
      </body>
    </html>
    """


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect dataset structure for FIREGUARD AI.")
    parser.add_argument("--dataset", type=Path, required=True, help="Dataset root directory")
    parser.add_argument("--output", type=Path, default=Path("reports"), help="Where to store report files")
    args = parser.parse_args()
    output_dir = args.output.resolve(); output_dir.mkdir(parents=True, exist_ok=True)

    report = inspect_dataset(args.dataset)
    json_path = output_dir / "dataset_report.json"
    html_path = output_dir / "dataset_report.html"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    html_path.write_text(build_html_report(report), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
