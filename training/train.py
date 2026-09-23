from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Train, validate, benchmark, and export ForestGuard YOLO.")
    parser.add_argument("--data", default="data/processed/data.yaml")
    parser.add_argument("--weights", default="yolo26n.pt")
    parser.add_argument("--scratch", action="store_true", help="Build from a YAML model instead of pretrained weights")
    parser.add_argument("--epochs", type=int, default=150); parser.add_argument("--batch", type=int, default=16); parser.add_argument("--imgsz", type=int, default=640); parser.add_argument("--patience", type=int, default=50); parser.add_argument("--device", default=None)
    args = parser.parse_args()
    model = YOLO("yolo26n.yaml" if args.scratch else args.weights)
    result = model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, patience=args.patience, device=args.device, project="runs/wildfire", name="forestguard", exist_ok=True)
    best = Path(result.save_dir) / "weights" / "best.pt"; Path("models").mkdir(exist_ok=True)
    if best.exists(): shutil.copy2(best, "models/wildfire_yolo.pt")
    metrics = model.val(data=args.data, imgsz=args.imgsz, device=args.device, verbose=False)
    start = time.perf_counter(); model.predict(source="data/processed/images/val", imgsz=args.imgsz, device=args.device, verbose=False, stream=False); seconds = time.perf_counter() - start
    box = metrics.box
    report = {"precision": float(box.mp), "recall": float(box.mr), "mAP50": float(box.map50), "mAP50-95": float(box.map), "params": "see Ultralytics model metadata", "FLOPs": "see model.info() for selected variant", "inference_FPS": "benchmark dependent; measured over validation directory", "validation_seconds": round(seconds, 3), "weights": "models/wildfire_yolo.pt"}
    Path("reports").mkdir(exist_ok=True); Path("reports/results.json").write_text(json.dumps(report, indent=2), encoding="utf-8"); print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
