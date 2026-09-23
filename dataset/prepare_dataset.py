from __future__ import annotations

import argparse
import io
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = ["fire", "smoke"]


def locate_label(image: Path, source: Path) -> Path | None:
    candidates = [image.with_suffix(".txt"), source / "labels" / image.relative_to(source).with_suffix(".txt")]
    return next((candidate for candidate in candidates if candidate.exists()), None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a local/Drive YOLO export into a clean fire/smoke dataset.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train", type=float, default=.7)
    parser.add_argument("--val", type=float, default=.2)
    args = parser.parse_args()
    import random, shutil
    images = [path for path in args.source.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS]
    if not images:
        raise SystemExit(f"No images found under {args.source}. Download/mount the Drive folder first.")
    random.Random(args.seed).shuffle(images)
    first = int(len(images) * args.train); second = int(len(images) * (args.train + args.val))
    splits = {"train": images[:first], "val": images[first:second], "test": images[second:]}
    classes = Counter(); true_negatives = 0; invalid = 0
    for split, members in splits.items():
        for index, image in enumerate(members):
            label = locate_label(image, args.source)
            stem = f"{image.stem}_{index:07d}"
            image_dir, label_dir = args.output / "images" / split, args.output / "labels" / split
            image_dir.mkdir(parents=True, exist_ok=True); label_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image, image_dir / f"{stem}{image.suffix.lower()}")
            content = label.read_text(encoding="utf-8", errors="ignore") if label else ""
            if not content.strip(): true_negatives += 1
            valid_lines = []
            for line in content.splitlines():
                fields = line.split()
                if len(fields) != 5 or not fields[0].isdigit(): invalid += 1; continue
                class_id = int(fields[0])
                if class_id >= len(CLASS_NAMES): invalid += 1; continue
                try:
                    values = [float(value) for value in fields[1:]]
                    if not all(0 <= value <= 1 for value in values): raise ValueError
                except ValueError: invalid += 1; continue
                classes[class_id] += 1; valid_lines.append(line)
            (label_dir / f"{stem}.txt").write_text("\n".join(valid_lines) + ("\n" if valid_lines else ""), encoding="utf-8")
    (args.output / "data.yaml").write_text(f"path: {args.output.resolve()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames: {CLASS_NAMES}\nnc: 2\n", encoding="utf-8")
    report = {"images": len(images), "splits": {key: len(value) for key, value in splits.items()}, "class_instances": {CLASS_NAMES[key]: value for key, value in classes.items()}, "true_negative_images": true_negatives, "invalid_labels": invalid, "warning": "No true-negative images found; false-alarm risk may be inflated." if true_negatives == 0 else None}
    (args.output / "dataset_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
