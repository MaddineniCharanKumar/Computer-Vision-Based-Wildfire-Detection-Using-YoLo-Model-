from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the ForestGuard YOLO detector with optional from-scratch mode.")
    parser.add_argument("--data", default="data/processed/data.yaml")
    parser.add_argument("--weights", default="yolo26n.pt")
    parser.add_argument("--scratch", action="store_true", help="Train a model from the YAML architecture without pre-trained weights")
    parser.add_argument("--epochs", type=int, default=150)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--patience", type=int, default=50)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    base_model = "yolo26n.yaml" if args.scratch else args.weights
    model = YOLO(base_model)
    result = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        device=args.device,
        project="runs/wildfire",
        name="forestguard",
        exist_ok=True,
    )

    best_path = Path(result.save_dir) / "weights" / "best.pt"
    Path("models").mkdir(exist_ok=True)
    if best_path.exists():
        shutil.copy2(best_path, "models/wildfire_yolo.pt")

    metrics = model.val(data=args.data, imgsz=args.imgsz, device=args.device, verbose=False)
    start = time.perf_counter()
    model.predict(source="data/processed/images/val", imgsz=args.imgsz, device=args.device, verbose=False, stream=False)
    elapsed = time.perf_counter() - start

    box = metrics.box
    report = {
        "precision": round(float(box.mp), 4),
        "recall": round(float(box.mr), 4),
        "mAP50": round(float(box.map50), 4),
        "mAP50_95": round(float(box.map), 4),
        "params": "Model-specific: inspect `model.model` or `model.info()` for exact parameter count.",
        "FLOPs": "Model-specific: inspect `model.info()` for FLOPs on your GPU/CPU hardware.",
        "inference_FPS": round(1.0 / max(elapsed, 1e-6), 2),
        "weights": "models/wildfire_yolo.pt",
    }
    Path("reports").mkdir(exist_ok=True)
    Path("reports/results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
