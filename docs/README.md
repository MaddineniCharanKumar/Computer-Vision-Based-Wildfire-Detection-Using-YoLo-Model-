# FIREGUARD AI

This repo contains a production-oriented wildfire detection and risk platform foundation. The design follows a modular architecture with dynamic dataset discovery, YOLO model adaptation, temporal verification, event tracking, and risk-aware early warning.

## Key modules

- `scripts/inspect_dataset.py`: dataset inspection and report generation
- `scripts/prepare_dataset.py`: dynamic dataset splitting
- `training/`: train, validate, evaluate, export, hyperparameters
- `fireguard/api.py`: FastAPI service
- `fireguard/analytics.py`: summaries and historical analytics
- `fireguard/alerts.py`: early warning and rule evaluation
- `fireguard/environment.py`: environmental provider abstraction
- `fireguard/risk.py`: risk scoring
- `fireguard/tracking.py`: tracking state and velocity tracking
- `utils/device.py`: hardware detection and precision configuration

## Important scientific limitations

- visual area proxy is not true fire size
- estimated direction is not propagation velocity
- environmental risk is not future certainty
- only real metrics are accepted
