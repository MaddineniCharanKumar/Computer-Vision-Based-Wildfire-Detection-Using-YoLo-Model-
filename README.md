# FIREGUARD AI

FIREGUARD AI is a research-oriented wildfire intelligence platform. It separates **FASDD model training data** from live monitoring sources and never treats demo values as real measurements.

## Dataset

FASDD source: https://www.scidb.cn/en/file?fid=9456106d26c5fc6b74143c3707115d39&mode=front

The local dataset is intentionally not committed. Inspect the actual files before preprocessing or training:

```powershell
python scripts\inspect_dataset.py --dataset "C:\Users\dines\Downloads\FASDD_UAV" --output reports
```

The command creates `reports/dataset_report.json` and `reports/dataset_report.html`. Counts, classes and annotation quality are only valid after running it against the downloaded dataset.

## Backend setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[ml,dev]"
Copy-Item .env.example .env
uvicorn fireguard.api:app --reload --host 0.0.0.0 --port 8000
```

API documentation: http://localhost:8000/docs

Useful endpoints:

```text
GET /api/health
GET /api/system/gpu
GET /api/dataset/statistics
GET /api/model/status
GET /api/environment/current
GET /api/fires
GET /api/alerts
GET /api/cameras
WebSocket /ws/live
```

The default non-demo environment provider returns `UNAVAILABLE` until a real provider is configured. It does not fabricate weather or sensor readings. Set `FIREGUARD_DEMO_MODE=true` only for clearly labelled local demonstrations.

## Dataset preparation and training

```powershell
python scripts\prepare_dataset.py --source "C:\Users\dines\Downloads\FASDD_UAV" --output data\processed
python training\train.py --data data\processed --weights yolo11n.pt --epochs 50 --batch 16 --device 0
python training\evaluate.py --weights runs\train\train\weights\best.pt --data data\processed\dataset.yaml --split val --device 0
```

Use `--device cpu` when CUDA is unavailable. Do not report metrics until the real evaluation command has completed.

## Dashboard

```powershell
cd dashboard
npm install
npm run dev
```

Open http://localhost:5173. The frontend must display unavailable/demo states from the API rather than inventing live detections.

## Docker

```powershell
docker compose up --build
```

The current Compose setup is suitable for local development. Production deployment still requires PostgreSQL, migrations, authentication, a live camera worker, provider credentials and a GPU-enabled runtime where applicable.

## Scientific limitations

The model detects visual fire/smoke patterns. Bounding-box size is a **Visual Fire Area Proxy**, spread is an apparent visual estimate, and the configurable risk score is decision support—not a physically validated wildfire propagation model. Never claim exact physical area, temperature, propagation speed, GPS, weather, accuracy or FPS unless measured from real data.
