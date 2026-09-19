# FIREGUARD AI

This repository is now a production-oriented foundation for wildfire intelligence. It includes modular API layers, dynamic device detection, risk scoring concepts, a practical dataset inspection workflow, and a dashboard front-end shell.

Use the real dataset inspection script before running model training or evaluation:

```bash
python scripts/inspect_dataset.py --dataset /path/to/fasdd --output reports
```

Then inspect the generated JSON report and continue to model configuration and training.
