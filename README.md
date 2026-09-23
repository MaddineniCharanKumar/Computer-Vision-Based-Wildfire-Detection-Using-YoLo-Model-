# ForestGuard Wildfire Intelligence

This project is built for local wildfire and smoke detection using YOLO on images and sampled video frames. Keep the dataset in your local machine or mounted Drive folder, not in GitHub.

## Project structure

- `dataset/prepare_dataset.py` — prepares a local wildfire dataset into YOLO format
- `training/train.py` — trains and validates YOLO wildfire detection models
- `fireguard/api.py` — FastAPI backend for image and video analysis
- `fireguard/runtime.py` — model wrapper and inference entry point
- `fireguard/severity.py` — wildfire severity logic (`none`, `smoke_only`, `small_fire`, `active_wildfire`)
- `dashboard/` — React dashboard for upload, thresholding, preview, and history

## Local setup

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 2) Install dependencies

```bash
pip install -e ".[ml,dev]"
```

### 3) Attach the dataset locally

Place the dataset in a local folder such as:

```text
D:/datasets/wildfire
```

or

```text
/data/wildfire
```

The dataset should contain image files and optional labels. The prep script will convert it to YOLO format and create `data/processed`.

### 4) Build the YOLO dataset

```bash
python dataset/prepare_dataset.py --source "D:/datasets/wildfire" --output data/processed
```

This will generate:

- `data/processed/images/train`
- `data/processed/images/val`
- `data/processed/images/test`
- `data/processed/labels/train`
- `data/processed/labels/val`
- `data/processed/labels/test`
- `data/processed/data.yaml`
- `data/processed/dataset_report.json`

### 5) Train the model

```bash
python training/train.py --data data/processed/data.yaml --weights yolo26n.pt --epochs 150 --batch 16 --imgsz 640
```

For a scratch model:

```bash
python training/train.py --data data/processed/data.yaml --weights yolo26n.pt --scratch --epochs 150 --batch 16 --imgsz 640
```

The best model is saved to:

```text
models/wildfire_yolo.pt
```

### 6) Start the backend

```bash
cp .env.example .env
uvicorn fireguard.api:app --reload --host 0.0.0.0 --port 8000
```

### 7) Start the frontend

```bash
cd dashboard
npm install
npm run dev
```

Set the API base if needed:

```env
VITE_API_BASE=http://localhost:8000
```

## Dataset notes

- Do not commit large image folders, label folders, or trained weights to GitHub.
- The project expects a local dataset path and will warn if there are no true-negative images.
- Use `data/processed` local output for training, which is much easier and faster than training directly from the full raw drive folder.

## API

- `POST /api/analyze?confidenceThreshold=0.35` — upload an image or video file
- `GET /api/history` — recent detection log
- `GET /api/model/status` — model health and path
- `GET /api/health` — backend status

## Severity levels

- `none`
- `smoke_only`
- `small_fire`
- `active_wildfire`

## Important

For real deployment, confirm the local dataset has no-fire images, otherwise false alarms may be inflated. The project will flag this in its dataset report.
