from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import Counter
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = ["fire", "smoke"]


def find_label(image: Path, source: Path) -> Path | None:
    candidates = [image.with_suffix(".txt"), source / "labels" / image.relative_to(source).with_suffix(".txt")]
    return next((p for p in candidates if p.exists()), None)


def prepare(source: Path, output: Path, seed: int = 42, train_ratio: float = .7, val_ratio: float = .2) -> dict:
    images = sorted(p for p in source.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise SystemExit(f"No images found below {source}. Mount/copy the Drive dataset first.")
    random.Random(seed).shuffle(images)
    cut1, cut2 = int(len(images) * train_ratio), int(len(images) * (train_ratio + val_ratio))
    groups = {"train": images[:cut1], "val": images[cut1:cut2], "test": images[cut2:]}
    counts = Counter(); negatives = 0
    for split, files in groups.items():
        for index, image in enumerate(files):
            stem = f"{image.stem}_{index:06d}"
            image_dir, label_dir = output / "images" / split, output / "labels" / split
            image_dir.mkdir(parents=True, exist_ok=True); label_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image, image_dir / f"{stem}{image.suffix.lower()}")
            label = find_label(image, source)
            if label and label.read_text(encoding="utf-8", errors="ignore").strip():
                content = label.read_text(encoding="utf-8", errors="ignore")
                (label_dir / f"{stem}.txt").write_text(content, encoding="utf-8")
                for line in content.splitlines():
                    parts = line.split()
                    if parts and parts[0].isdigit(): counts[int(parts[0])] += 1
            else:
                (label_dir / f"{stem}.txt").write_text("", encoding="utf-8")
                negatives += 1
    yaml = output / "data.yaml"
    yaml.write_text(f"path: {output.resolve()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames: {CLASS_NAMES}\nnc: 2\n", encoding="utf-8")
    report = {"images": len(images), "splits": {k: len(v) for k, v in groups.items()}, "class_instances": {CLASS_NAMES[k] if k < 2 else str(k): v for k, v in counts.items()}, "true_negative_images": negatives, "warning": "No true-negative images found; false-alarm risk may be inflated." if negatives == 0 else None}
    (output / "dataset_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2)); return report


def main():
    p = argparse.ArgumentParser(description="Prepare YOLO fire/smoke data from a mounted Drive folder or YOLO export.")
    p.add_argument("--source", type=Path, required=True); p.add_argument("--output", type=Path, default=Path("data/processed")); p.add_argument("--seed", type=int, default=42)
    a = p.parse_args(); prepare(a.source, a.output, a.seed)


if __name__ == "__main__": main()
