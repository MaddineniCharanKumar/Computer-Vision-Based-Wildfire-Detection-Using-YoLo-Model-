# FIREGUARD AI

Production-focused wildfire intelligence stack for dataset inspection, detection, temporal verification, risk estimation, alerts and dashboard monitoring.

## 1. Dataset inspection

Before any training or inference, inspect the real dataset:

```bash
python scripts/inspect_dataset.py --dataset /path/to/fasdd --output reports
```

This produces:
- `reports/dataset_report.json`
- `reports/dataset_report.html`

It automatically detects:
- image counts
- annotation file counts
- YOLO / VOC/XML / COCO/JSON formats
- missing labels
- orphan labels
- duplicates
- corrupted files
- invalid bounding boxes

## 2. Prepare data

```bash
python scripts/setup_project.py
python scripts/prepare_dataset.py --source /path/to/fasdd --output data/processed
```

## 3. Train

```bash
python training/train.py --data data/processed/dataset.yaml --weights yolo11n.pt --epochs 50 --batch 16
```

## 4. Evaluate

```bash
python training/evaluate.py --weights runs/train/exp/weights/best.pt --data data/processed/dataset.yaml
```

## 5. Run API

```bash
uvicorn fireguard.api:app --reload
```

## Scientific limitations

- bounding-box area is a visual proxy, not true fire area
- spread direction is estimated visual motion, not true propagation
- risk score is an environmental-visual estimate, not future certainty
- no fake metrics, no fake weather, no fake GPS, no fake GPU telemetry
