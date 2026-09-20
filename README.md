# EcoSpread-YOLO

EcoSpread-YOLO is a research prototype for real-time UAV wildfire detection and predictive wildfire intelligence. It combines a lightweight YOLO-based detector, environmental telemetry, geospatial context, and short-horizon spread forecasting in a modular backend architecture.

## Mission

Move from reactive visual fire detection toward predictive wildfire intelligence by integrating:
- YOLO fire/smoke detection
- UAV geolocation and telemetry
- live or recent environmental data
- satellite corroboration
- terrain and vegetation context
- risk scoring and alerting
- short-horizon spread forecasts

## Core requirements enforced by this project

- No fabricated detections, fire events, GPS, weather values, or evaluation metrics.
- Demo-mode must be explicit and clearly labeled.
- Environmental data must preserve freshness metadata and source information.
- If a provider is missing, the system must report UNAVAILABLE instead of inventing data.
- All model and evaluation claims must be based on actual runs, not placeholders.
- The code must remain modular and testable.

## Repository structure

- `fireguard/` — backend, configuration, runtime, and service logic
- `training/` — dataset validation, training, evaluation, and export scripts
- `scripts/` — dataset preparation and inspection helpers
- `dashboard/` — frontend for map, alert, risk, and telemetry visualization
- `docs/` — architecture and operational notes
- `tests/` — unit and API tests

## Local development

1. Create a virtual environment
2. Install dependencies
3. Copy `.env.example` to `.env`
4. Start the API

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[ml,dev]"
cp .env.example .env
uvicorn fireguard.api:app --reload --host 0.0.0.0 --port 8000
```

API docs:
- http://localhost:8000/docs

## Key endpoints

- GET `/api/health`
- GET `/api/system/gpu`
- GET `/api/model/status`
- POST `/api/detection/image`
- POST `/api/detection/video`
- GET `/api/cameras`
- POST `/api/camera/{id}/start`
- POST `/api/camera/{id}/stop`
- GET `/api/fires`
- GET `/api/fires/{id}`
- GET `/api/environment/current`
- GET `/api/environment/history`
- GET `/api/risk/{event_id}`
- GET `/api/alerts`
- POST `/api/alerts/{id}/acknowledge`
- GET `/api/analytics/overview`
- WebSocket `/ws/live`

## Data and evaluation policy

- Dataset inspection must happen before training or metric reporting.
- No model metrics may be reported without real validation data and actual execution.
- Do not parse bounding-box area as precise physical fire area unless calibration supports it.
- Keep research modules isolated and configurable.

## Deployment note

The project supports GPU acceleration when available, but it must continue safely on CPU or with unavailable providers. It must degrade gracefully and clearly report missing resources instead of generating fake results.
