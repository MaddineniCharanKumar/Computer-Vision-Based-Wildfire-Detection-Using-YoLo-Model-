from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from ultralytics import YOLO


def main():
    p = argparse.ArgumentParser(description="Train and evaluate the ForestGuard YOLO detector.")
    p.add_argument("--data", default="data/processed/data.yaml"); p.add_argument("--weights", default="yolo26n.pt", help="Pretrained checkpoint; use --scratch for a new model")
    p.add_argument("--scratch", action="store_true"); p.add_argument("--epochs", type=int, default=150); p.add_argument("--batch", type=int, default=16); p.add_argument("--imgsz", type=int, default=640); p.add_argument("--device", default=None); p.add_argument("--patience", type=int, default=50)
    a = p.parse_args(); model = YOLO(a.weights if not a.scratch else "yolo26n.yaml")
    results = model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch, patience=a.patience, device=a.device, project="runs/wildfire", name="forestguard", exist_ok=True)
    best = Path(results.save_dir) / "weights" / "best.pt"; Path("models").mkdir(exist_ok=True)
    if best.exists(): shutil.copy2(best, "models/wildfire_yolo.pt")
    metrics = model.val(data=a.data, imgsz=a.imgsz, device=a.device, verbose=False)
    box = metrics.box
    report = {"precision": float(box.mp), "recall": float(box.mr), "mAP50": float(box.map50), "mAP50_95": float(box.map), "weights": "models/wildfire_yolo.pt", "note": "FLOPs and FPS depend on hardware; run inference benchmarking before publishing them."}
    Path("reports").mkdir(exist_ok=True); Path("reports/results.json").write_text(json.dumps(report, indent=2), encoding="utf-8"); print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
