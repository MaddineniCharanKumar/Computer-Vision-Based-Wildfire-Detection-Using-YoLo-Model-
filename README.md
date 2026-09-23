# ForestGuard Wildfire Intelligence

This project is for a local wildfire detector built with YOLO, using either:
- a labeled dataset (images + labels), or
- an images-only dataset (with a warning that training will not be meaningful without annotations)

## Important: dataset size

Do not commit large datasets, images, training folders, or model weights to GitHub. Keep the raw files on your local machine and run the preparation script locally.

## Local setup

### 1) Create a venv and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[ml,dev]"
```

### 2) Put your dataset locally

Example folder:

```text
D:/datasets/wildfire
```

or

```text
C:/Users/YourName/Desktop/wildfire_dataset
```

If the dataset contains only images, the script will still create the YOLO structure, but each image will get an empty `.txt` label file unless real annotations exist.

### 3) Prepare the dataset

```bash
python dataset/prepare_dataset.py --source "D:/datasets/wildfire" --output data/processed
```

This creates:

- `data/processed/images/train`
- `data/processed/images/val`
- `data/processed/images/test`
- `data/processed/labels/train`
- `data/processed/labels/val`
- `data/processed/labels/test`
- `data/processed/data.yaml`
- `data/processed/dataset_report.json`

### 4) Train the YOLO model

```bash
python training/train.py --data data/processed/data.yaml --weights yolo26n.pt --epochs 150 --batch 16 --imgsz 640
```

For a from-scratch run:

```bash
python training/train.py --data data/processed/data.yaml --weights yolo26n.pt --scratch --epochs 150 --batch 16 --imgsz 640
```

### 5) Run backend

```bash
cp .env.example .env
uvicorn fireguard.api:app --reload --host 0.0.0.0 --port 8000
```

### 6) Run frontend

```bash
cd dashboard
npm install
npm run dev
```

## Notes for images-only folders

If you only have raw images and no labels, the project will still generate compatible YOLO folders, but training will not be meaningful until the dataset is annotated with fire/smoke boxes.

The script prints a warning like:

```text
This dataset has no labels. All images are treated as empty-label samples. You must add bounding-box annotations for fire/smoke to train a usable model.
```

This is expected for an unlabeled image-only dataset.

## Required local data policy

- Keep raw images locally
- Keep labels locally
- Do not push the dataset to GitHub
- Only version code, configs, and small generated logs
