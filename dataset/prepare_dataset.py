from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import Counter
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = ["fire", "smoke"]


def find_label_path(image: Path, source_root: Path) -> Path | None:
    candidates = [
        image.with_suffix(".txt"),
        source_root / "labels" / image.relative_to(source_root).with_suffix(".txt"),
        source_root / "Annotations" / image.relative_to(source_root).with_suffix(".txt"),
        source_root / "YOLO" / image.relative_to(source_root).with_suffix(".txt"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def build_dataset(source: Path, output: Path, seed: int = 42, train_ratio: float = 0.7, val_ratio: float = 0.2) -> dict:
    source = source.resolve()
    images = sorted(path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise SystemExit(
            f"No image files were found under '{source}'. "
            "Place your image folder locally (for example D:/datasets/wildfire) and rerun the command."
        )

    random.Random(seed).shuffle(images)
    cutoff_1 = int(len(images) * train_ratio)
    cutoff_2 = int(len(images) * (train_ratio + val_ratio))
    splits = {
        "train": images[:cutoff_1],
        "val": images[cutoff_1:cutoff_2],
        "test": images[cutoff_2:],
    }

    class_counts = Counter()
    true_negative_images = 0
    invalid_label_lines = 0
    total_annotations = 0

    for split_name, members in splits.items():
        image_dir = output / "images" / split_name
        label_dir = output / "labels" / split_name
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

        for index, image_path in enumerate(members):
            safe_name = f"{image_path.stem}_{index:06d}{image_path.suffix.lower()}"
            shutil.copy2(image_path, image_dir / safe_name)

            label_path = find_label_path(image_path, source)
            output_label = label_dir / f"{Path(safe_name).stem}.txt"
            if label_path and label_path.exists():
                content = label_path.read_text(encoding="utf-8", errors="ignore")
            else:
                content = ""

            cleaned_lines = []
            for line in content.splitlines():
                fields = line.strip().split()
                if len(fields) != 5:
                    invalid_label_lines += 1
                    continue
                try:
                    cls_id = int(fields[0])
                    values = [float(value) for value in fields[1:]]
                    if not all(0.0 <= value <= 1.0 for value in values):
                        raise ValueError
                except ValueError:
                    invalid_label_lines += 1
                    continue
                if cls_id < 0 or cls_id >= len(CLASS_NAMES):
                    invalid_label_lines += 1
                    continue
                class_counts[cls_id] += 1
                total_annotations += 1
                cleaned_lines.append(line.strip())

            if not cleaned_lines:
                true_negative_images += 1

            output_label.write_text("\n".join(cleaned_lines) + ("\n" if cleaned_lines else ""), encoding="utf-8")

    yaml_text = (
        f"path: {output.resolve()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        f"names: [{', '.join(CLASS_NAMES)}]\n"
        "nc: 2\n"
    )
    (output / "data.yaml").write_text(yaml_text, encoding="utf-8")

    warning = None
    if total_annotations == 0:
        warning = (
            "This dataset has no labels. All images are treated as empty-label samples. "
            "You must add bounding-box annotations for fire/smoke to train a usable model."
        )
    elif true_negative_images == len(images):
        warning = "No true-negative images were found. False-alarm risk may be inflated in deployment."

    report = {
        "images": len(images),
        "splits": {k: len(v) for k, v in splits.items()},
        "class_instances": {CLASS_NAMES[k]: v for k, v in sorted(class_counts.items())},
        "total_annotations": total_annotations,
        "true_negative_images": true_negative_images,
        "invalid_labels": invalid_label_lines,
        "warning": warning,
    }
    (output / "dataset_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare a local wildfire dataset into YOLO format. Supports both labeled and images-only folders."
    )
    parser.add_argument("--source", type=Path, required=True, help="Local dataset folder or mounted Drive folder")
    parser.add_argument("--output", type=Path, default=Path("data/processed"), help="Output directory for prepared YOLO dataset")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train", type=float, default=0.7)
    parser.add_argument("--val", type=float, default=0.2)
    args = parser.parse_args()
    build_dataset(args.source, args.output, args.seed, args.train, args.val)


if __name__ == "__main__":
    main()
