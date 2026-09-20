# EcoSpread-YOLO

EcoSpread-YOLO is a research prototype for real-time UAV wildfire detection and predictive wildfire intelligence. The project focuses on a lightweight YOLO-based detector, environmental fusion, and short-horizon spread forecasting rather than reactive-only fire localization.

## Goals

- Detect fire and smoke in UAV imagery using a configurable YOLO-family model.
- Fuse detections with UAV telemetry, weather, terrain, vegetation, and satellite context.
- Produce short-horizon spread forecasts with explicit uncertainty.
- Expose system state through a modular API and live dashboard.
- Keep every claim tied to real measurements and actual evaluations.

## Core project rules

- No fabricated detections, GPS coordinates, weather values, satellite observations, or evaluation metrics.
- Keep DEMO_MODE explicit and clearly labeled when simulation is intentionally enabled.
- Treat environmental data freshness as a first-class signal: LIVE, RECENT, STALE, or UNAVAILABLE.
- Require real model weights and real data before reporting model performance.
- Keep research and production code separated so experimental modules can be enabled or disabled.

## Relevant repository structure

- `fireguard/` — Python backend and service layer.
- `training/` — training, validation, and export scripts.
- `scripts/` — dataset validation and preparation utilities.
- `dashboard/` — optional dashboard frontend.
- `docs/` — setup and architecture documentation.
- `tests/` — backend and API tests.

## Operational constraints

- Prefer real providers over hard-coded demo data.
- Guard all external APIs with explicit failure handling and logging.
- Keep configuration externalized in environment variables and `.env.example`.
- Do not commit secrets or private credentials.
- Do not present bounding-box area as exact physical fire area unless calibration supports it.

## Minimum implementation standard

The codebase should support:
- a FastAPI backend with health/system/model endpoints;
- environment and provider abstractions;
- modular detection, risk, and alert services;
- no fake data in default runtime responses;
- structured logging and safe degradation when dependencies are unavailable.

## Development expectation

When adding code, prefer the smallest coherent change that follows the architecture, keeps modules testable, and does not invent unavailable APIs or SDK methods.
