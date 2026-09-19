# FIREGUARD AI

Production-oriented wildfire intelligence platform: dataset inspection, dynamic YOLO training/inference, temporal verification, visual growth/spread proxies, environmental fusion, risk/early-warning alerts, and a live API.

> **Important:** This repository never fabricates dataset statistics, weather, GPS, GPU telemetry, or model metrics. Run the inspector and evaluation commands against real inputs before making operational decisions.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
python scripts/inspect_dataset.py --dataset data/raw --output reports
uvicorn fireguard.api:app --reload
```

The API starts in clearly labelled demo mode when `FIREGUARD_DEMO_MODE=true`; simulated values are never mixed with real providers.

## Workflow

1. `scripts/inspect_dataset.py` discovers formats/classes and writes `reports/dataset_report.json` and `.html`.
2. `scripts/prepare_dataset.py` validates and splits data dynamically, preserving YOLO labels.
3. `python -m training.train --data data/processed/dataset.yaml` trains the discovered classes.
4. `python -m training.evaluate --weights runs/.../best.pt` writes real metrics only.
5. `uvicorn fireguard.api:app` exposes health, detection, risk, alerts, environmental, GPU and WebSocket endpoints.

See `docs/` for architecture, limitations, deployment and API details.
