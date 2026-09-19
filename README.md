# FIREGUARD AI

The repository is code-only. Your local FASDD dataset is configured at `C:\Users\dines\Downloads\FASDD_UAV` and is never copied into GitHub.

## Inspect your local dataset

From this repository root in VS Code PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\inspect_dataset.py --dataset "C:\Users\dines\Downloads\FASDD_UAV" --output reports
```

Or use the configured default path:

```powershell
python scripts\inspect_dataset.py --output reports
```

Open these generated files after inspection:

- `reports/dataset_report.json`
- `reports/dataset_report.html`

The inspector reads files in place and reports actual counts, annotation formats, classes, missing/orphan labels, corrupted files, duplicates, and invalid boxes. It does not invent dataset statistics.

## Continue after inspection

Only after reviewing the report, prepare and train using the real discovered structure:

```powershell
python scripts\prepare_dataset.py --source "C:\Users\dines\Downloads\FASDD_UAV" --output data\processed
python training\train.py --data data\processed --weights yolo11n.pt --epochs 50 --batch 2 --device cpu
```

Training on a 13.5 GB dataset using CPU can be very slow. Use a cloud or NVIDIA GPU machine for practical training.
