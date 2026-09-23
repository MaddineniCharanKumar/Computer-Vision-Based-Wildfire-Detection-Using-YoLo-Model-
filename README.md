# ForestGuard — Wildfire & Smoke Detection

ForestGuard is an evidence-first YOLO application for detecting **fire** and **smoke** in images and sampled video frames. It does not claim trained metrics or fabricate detections when weights or data are unavailable.

## Dataset from Google Drive

Download the shared Drive folder locally or mount it in Colab, then inspect it:

```bash
python scripts/inspect_dataset.py --dataset /path/to/downloaded/folder --output reports
python dataset/prepare_dataset.py --source /path/to/downloaded/folder --output data/processed
```

The preparation script creates `images/`, `labels/`, `data.yaml`, class counts, split counts, and warns when no true-negative images are present. Do not commit the downloaded dataset or model weights.

## Train

The default is the lightweight `yolo26n` configuration. Select a larger checkpoint only after checking your GPU budget:

```bash
pip install -e ".[ml,dev]"
python training/train.py --data data/processed/data.yaml --weights yolo26n.pt --epochs 150 --batch 16
# Training from scratch:
python training/train.py --data data/processed/data.yaml --scratch
```

Best weights are copied to `models/wildfire_yolo.pt`; real evaluation output is written to `reports/results.json`. Metrics are never reported until validation actually runs.

## Backend

```bash
cp .env.example .env
uvicorn fireguard.api:app --reload --host 0.0.0.0 --port 8000
```

`POST /api/analyze` accepts images and videos. Videos are sampled at `FIREGUARD_FRAME_INTERVAL_SECONDS` (default one second). Use `?confidenceThreshold=0.5`. Results contain bounding boxes, class, confidence, per-frame severity, aggregate severity, and history is available at `GET /api/history`.

Severities: `none`, `smoke_only`, `small_fire`, `active_wildfire`. Webhook alerts for active wildfire are optional and rate-limited by `FIREGUARD_ALERT_COOLDOWN_SECONDS`.

## Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Set `VITE_API_BASE=http://localhost:8000` in `dashboard/.env`. The dashboard includes image/video upload, confidence control, canvas-style bounding-box visualization, severity cards, and detection history. Keep the existing telemetry pages for optional weather, satellite, and geospatial integrations.
