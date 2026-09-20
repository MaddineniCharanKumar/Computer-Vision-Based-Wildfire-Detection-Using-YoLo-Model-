# EcoSpread-YOLO — GitHub Copilot Project Instructions

## Project identity

**Project:** EcoSpread-YOLO  
**Goal:** Build a real-time UAV wildfire detection and environment-aware spread prediction system.

The system must move beyond fire localization and combine:
1. Lightweight YOLO-based fire/smoke detection.
2. UAV geolocation and telemetry.
3. Real-time environmental data.
4. Satellite active-fire corroboration.
5. Terrain and vegetation/fuel information.
6. Physics-informed and/or learning-based fire-spread prediction.
7. Real-time risk assessment, visualization, and alerting.

The proposal describes the intended research direction as a transition from reactive detection to predictive wildfire intelligence.

## Core research gap

The project proposal identifies a common limitation in recent UAV fire detectors: they focus on detecting where fire is now but do not model where it may spread or fuse live environmental telemetry with the vision pipeline.

EcoSpread-YOLO should therefore treat environmental fusion and short-horizon spread prediction as first-class components rather than optional dashboard features.

## Reference detector ideas

The proposal builds upon ideas from:
- AHE-YOLO
- FF-Mamba-YOLO
- ASCA-YOLO
- Fire-YOLO26

When implementing these ideas, do not claim that a module has been reproduced exactly unless its source implementation and equations are available. Keep experimental modules isolated and configurable.

Candidate components from the proposal:
- ADown-style adaptive/hybrid downsampling.
- EMBC or FWAMSConv-style efficient multi-scale convolution.
- FWSCSAttention-style context-saliency attention.
- Optional RGB + thermal-infrared fusion using a T-FAM-style design.

The base detector should remain lightweight and suitable for UAV/edge deployment.

## System pipeline

Implement the architecture as:

UAV camera / RGB-Thermal input
→ YOLO fire/smoke detection
→ temporal filtering/tracking
→ UAV GPS/IMU geolocation
→ real-time environmental/geospatial data ingestion
→ environmental + terrain + vegetation fusion
→ fire-spread prediction
→ risk assessment
→ predicted fire perimeter
→ map dashboard
→ alerting
→ logging and evaluation

Keep each stage modular so that detector, environmental providers, spread models, and dashboard components can be tested independently.

## Detection requirements

Use a configurable lightweight YOLO-family detector.

Required capabilities:
- Training and inference on NVIDIA GPU when available.
- Configurable image size, batch size, epochs, optimizer, learning rate, augmentation, checkpoints, and resume.
- Support image, video, webcam, RTSP/network camera, and UAV video inputs where practical.
- Track confidence, class, bounding box, timestamp, source/camera ID, and inference latency.
- Support optional thermal input without forcing thermal hardware to exist.
- Preserve the ability to run RGB-only.

Do not hard-code dataset classes before inspecting the actual dataset and annotation files.

## Dataset handling

Before training:
1. Inspect directory structure.
2. Detect annotation format.
3. Identify class names and IDs from the actual annotations/configuration.
4. Validate image-label correspondence.
5. Detect corrupted/unreadable images.
6. Detect invalid or out-of-range bounding boxes.
7. Report class distribution.
8. Create reproducible train/validation/test splits when a valid split is not already provided.
9. Prevent data leakage between splits.

Never fabricate dataset counts or evaluation metrics.

## Geolocation

Every detection should be associated with the best available geographic information.

Inputs may include:
- UAV GPS.
- UAV IMU.
- Camera intrinsics.
- UAV altitude.
- Camera orientation/attitude.

The implementation must clearly distinguish:
- Actual GPS coordinates.
- Estimated/projected coordinates.
- Missing location.

Never invent coordinates.

## Real-time environmental data

Environmental data is a core production component.

The system should support real external sources such as:
- Weather APIs.
- NOAA or equivalent weather feeds where applicable.
- Local IoT weather stations.
- MQTT sensor streams.
- REST sensor endpoints.
- WebSocket sensor streams.

The proposal explicitly identifies:
- Wind speed.
- Wind direction.
- Temperature.
- Relative humidity.
- Precipitation.

The architecture should also be extensible for:
- Fuel moisture.
- Soil moisture.
- Vegetation/fuel condition.
- Air quality.
- Visibility.
- Atmospheric pressure.
- Solar radiation.

Every environmental observation should carry:
- timestamp
- source/provider
- location/camera association
- sensor ID when available
- value
- unit
- freshness/status

Never silently treat stale environmental data as live.

Recommended freshness states:
- LIVE
- RECENT
- STALE
- UNAVAILABLE

If an external provider fails:
- Continue fire detection if possible.
- Mark environmental data unavailable/stale.
- Do not substitute fabricated readings.
- Log the provider failure.

Respect API rate limits. Use configurable polling intervals and caching where appropriate.

## Environmental/geospatial fusion

At each geolocated detection:
1. Determine the observation location.
2. Retrieve the latest valid environmental state.
3. Retrieve relevant terrain information.
4. Retrieve relevant vegetation/fuel information when available.
5. Retrieve satellite active-fire information where configured.
6. Normalize units and timestamps.
7. Associate all inputs with the fire event.
8. Recalculate risk/spread inputs.
9. Persist the fused state.
10. Broadcast updates to the dashboard.

## Satellite corroboration

The proposal identifies NASA FIRMS (VIIRS/MODIS) near-real-time active-fire hotspots as a corroboration source.

Use satellite data to:
- Cross-check detections.
- Provide additional spatial context.
- Help reduce false alarms.

Do not treat satellite observations as ground truth automatically. Record source, acquisition/observation time, spatial uncertainty, and data age when available.

## Terrain and vegetation

Terrain features may include:
- Elevation.
- Slope.
- Aspect.

Candidate sources in the proposal:
- SRTM.
- ASTER DEM.

Vegetation/fuel features may include:
- NDVI.
- Land-cover classification.
- Fuel-moisture proxy.

Candidate sources in the proposal:
- Sentinel-2.
- Landsat.

Clearly label proxies. NDVI or another remote-sensing index must not automatically be represented as direct fuel moisture unless validated.

## Fire-spread prediction

This is the core novelty.

Support three model families:

### 1. Physics-informed
Possible approaches:
- Rothermel-type fire-spread formulation.
- Cellular automata.

Inputs can include:
- Current fire location/perimeter.
- Wind vector.
- Slope.
- Aspect.
- Fuel type.
- Fuel moisture.

### 2. Data-driven
Possible approaches:
- LSTM.
- ConvLSTM.
- Graph neural network.

Train using historical fire-progression sequences paired with environmental sequences when suitable data exists.

### 3. Hybrid
Preferred research architecture:
- Physics/CA model produces a physically grounded short-horizon estimate.
- A learned correction model adjusts local/model mismatch.
- The system produces the final forecast perimeter.

Keep the physics model and learned correction model separately testable.

## Forecasting horizon

The proposal uses a short-horizon target such as:
- t + 30 minutes
- t + 60 minutes

Do not present forecasts as guaranteed outcomes.

Every forecast should record:
- forecast generation time
- horizon
- input observation time
- model version
- predicted perimeter/polygon
- confidence/uncertainty when supported
- environmental state used

## Fire representation

Maintain a fire-event object containing at minimum:
- event ID
- source/camera ID
- detection timestamps
- geographic position
- current detection geometry
- current confidence
- environmental state
- terrain state
- vegetation/fuel state
- predicted perimeter
- forecast horizon
- risk state
- alert state
- model versions

If bounding-box area is used, call it a visual-area proxy unless camera geometry/calibration supports physical-area estimation.

Do not claim exact fire size, propagation speed, or future trajectory without appropriate calibration and validation.

## Risk and alerting

The dashboard should provide a risk-level classification based on the implemented model.

Risk should be explainable. Where applicable, expose contributing factors such as:
- detection confidence
- persistence
- observed growth
- wind
- humidity
- temperature
- precipitation
- terrain
- fuel/vegetation condition
- satellite corroboration

Avoid arbitrary scientific claims. Any thresholds or weights should be configurable and explicitly described as engineering choices unless scientifically validated.

Alerts should contain:
- event ID
- alert level
- timestamp
- location
- reason
- contributing signals
- model/version information
- acknowledgement status

Support alert deduplication and cooldowns.

## Real-time dashboard

Build a map-oriented dashboard showing:
- Live UAV/camera detections.
- Current fire locations.
- Current environmental readings.
- Terrain/vegetation context where available.
- Satellite hotspot context where available.
- Predicted spread perimeter for 30/60 minutes.
- Risk state.
- Alert history.
- Detection FPS/latency.
- System/provider health.

The dashboard must distinguish:
- live data
- recent data
- stale data
- unavailable data

Do not display demo/simulated values as real observations.

## Backend architecture

Use a modular service architecture.

Recommended components:
- Detection service.
- Tracking/temporal verification service.
- Telemetry/geolocation service.
- Environmental provider layer.
- Satellite provider layer.
- Terrain/vegetation data layer.
- Spread prediction service.
- Risk service.
- Alert service.
- Persistence layer.
- WebSocket/live update layer.
- REST API layer.

Python/FastAPI is suitable for the backend.

Use clear separation between:
- API/controller layer
- service/business logic
- data/provider adapters
- model layer
- persistence/repository layer

## API expectations

Provide endpoints along the lines of:

- GET /api/health
- GET /api/system/gpu
- GET /api/model/status
- POST /api/detection/image
- POST /api/detection/video
- GET /api/cameras
- POST /api/camera/{id}/start
- POST /api/camera/{id}/stop
- GET /api/fires
- GET /api/fires/{id}
- GET /api/environment/current
- GET /api/environment/history
- GET /api/risk/{event_id}
- GET /api/alerts
- POST /api/alerts/{id}/acknowledge
- GET /api/analytics/overview

Adapt endpoint names to the actual implementation rather than creating unused placeholder APIs.

## WebSocket/live updates

Provide a WebSocket channel for live events, for example:

/ws/live

Possible messages:
- detection update
- track update
- fire-event update
- environmental update
- spread forecast update
- risk update
- alert
- camera status
- provider status
- GPU/FPS status

Use structured JSON messages with event type, timestamp, source, and payload.

## Database

Use a relational database such as PostgreSQL.

Suggested entities:
- camera_sources
- fire_events
- detections
- tracks
- environmental_readings
- risk_scores
- alerts
- model_versions
- inference_logs
- sensor_sources
- notification_logs

Use migrations and indexes for:
- event ID
- camera ID
- timestamp
- geographic lookup fields where appropriate

Do not store secrets in the database unless explicitly required and securely protected.

## GPU and edge deployment

The project should support NVIDIA GPU acceleration.

Monitor:
- GPU availability
- CUDA availability
- GPU memory
- utilization where available
- inference latency
- FPS

Use FP16/mixed precision where compatible.

Optional deployment targets:
- NVIDIA desktop/server GPU.
- Jetson-class edge hardware.

If full spread prediction is too expensive for onboard execution, follow the proposal's split architecture:
- latency-critical detection onboard
- heavier spread prediction on a ground station or connected edge server

Do not assume a particular NVIDIA GPU model is available.

## Evaluation

Detection metrics:
- mAP@0.5
- mAP@0.5:0.95
- Precision
- Recall

Efficiency metrics:
- parameter count
- FLOPs
- model size
- FPS
- inference latency

Spread metrics:
- perimeter IoU at t+30
- perimeter IoU at t+60
- fire-front position RMSE

System metrics:
- detection-to-alert end-to-end latency
- environmental data latency/freshness
- edge/onboard FPS
- power draw where hardware measurement is available

All reported metrics must come from actual experiments. Never fabricate results.

## Research experiments

Keep baseline and ablation configurations reproducible.

Useful comparisons:
1. Base YOLO detector.
2. Detector + selected lightweight modules.
3. Detector + temporal/tracking logic.
4. Detector + environmental fusion.
5. Physics/CA spread model.
6. Data-driven spread model.
7. Hybrid physics + learned correction model.

Report actual results and limitations.

## Reliability rules

- No fake detections.
- No fake environmental values.
- No fake GPS.
- No fake satellite observations.
- No fake GPU metrics.
- No fake evaluation scores.
- No hidden fallback from live data to simulated data.
- Clearly label DEMO MODE when simulation is intentionally enabled.
- Preserve timestamps and source metadata.
- Log failures instead of silently masking them.

## Testing

Implement:
- Unit tests for detector adapters.
- Unit tests for environmental providers.
- Unit tests for geolocation transformations.
- Unit tests for spread-model calculations.
- API tests.
- WebSocket tests.
- Database integration tests.
- End-to-end pipeline tests.

Test failure scenarios:
- camera disconnected
- invalid telemetry
- missing GPS
- weather API unavailable
- stale weather
- satellite service unavailable
- malformed sensor data
- GPU unavailable
- model unavailable
- database unavailable

## Configuration

Use environment variables/configuration files for:
- model path
- device (cuda/cpu)
- camera/RTSP URL
- database URL
- weather provider
- API credentials
- polling intervals
- satellite provider
- DEM source
- vegetation source
- alert thresholds
- forecast horizons

Never commit API keys, passwords, tokens, or private credentials.

Provide .env.example, not a real .env containing secrets.

## Code-generation behavior for GitHub Copilot

When generating code:
1. Inspect the existing project structure first.
2. Reuse existing abstractions instead of creating duplicates.
3. Make the smallest coherent change needed.
4. Keep provider-specific code behind interfaces/adapters.
5. Add tests for new business logic.
6. Add type hints to Python code.
7. Handle errors explicitly.
8. Add structured logging.
9. Keep configuration externalized.
10. Do not invent unavailable APIs or SDK methods.
11. Do not fabricate data just to make the UI appear populated.
12. Do not remove existing functionality unless explicitly requested.
13. Prefer production-ready implementations over pseudo-code.
14. Keep research/experimental modules isolated so they can be enabled or disabled.
15. Explain assumptions in code comments or documentation when the source proposal does not specify an implementation detail.

## Documentation

Maintain:
- README
- architecture documentation
- setup instructions
- environment configuration
- dataset preparation instructions
- training instructions
- inference instructions
- live UAV/RTSP instructions
- environmental-provider setup
- spread-model training/validation instructions
- API documentation
- testing instructions
- limitations and reproducibility notes

## Implementation priority

Implement in this order unless the user explicitly requests another sequence:

### Phase 1 — Baseline detection
- Dataset validation.
- YOLO baseline.
- GPU training/inference.
- Evaluation.

### Phase 2 — Real-time detection
- Camera/UAV/RTSP ingestion.
- Tracking/temporal filtering.
- Detection event storage.

### Phase 3 — Real-time data fusion
- Geolocation.
- Weather/environment providers.
- Satellite hotspot integration.
- Terrain.
- Vegetation/fuel information.

### Phase 4 — Spread prediction
- Physics/CA baseline.
- Historical validation.
- Learned correction.
- Hybrid model.

### Phase 5 — Dashboard and alerting
- Map visualization.
- Live WebSocket updates.
- Risk explanation.
- Alert lifecycle.

### Phase 6 — Evaluation and research packaging
- Ablation studies.
- Detection benchmarks.
- Spread benchmarks.
- End-to-end latency.
- Edge deployment tests.
- Reproducible documentation.

## Important scientific boundaries

The system is a research prototype unless independently validated for operational wildfire response.

Do not claim:
- guaranteed fire prediction
- guaranteed spread trajectory
- exact physical fire area from an uncalibrated bounding box
- exact fuel moisture from an index without validation
- exact fire-front speed without suitable ground truth
- operational safety certification

Clearly distinguish observations, estimates, model outputs, and forecasts.

## Proposal alignment

The implementation should preserve the proposal's central contribution:

> Couple a lightweight UAV fire detector with live environmental/geospatial telemetry and a physics-informed spread model to move from reactive fire detection toward predictive wildfire intelligence.

The expected system should remain focused on real-time UAV deployment, environmental fusion, short-horizon spread forecasting, and measurable evaluation.

