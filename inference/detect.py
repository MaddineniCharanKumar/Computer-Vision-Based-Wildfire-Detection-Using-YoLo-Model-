import argparse
from pathlib import Path
from PIL import Image
from fireguard.runtime import FireguardRuntime

parser = argparse.ArgumentParser(description="Run ForestGuard detection on an image.")
parser.add_argument("source"); parser.add_argument("--weights", default="models/wildfire_yolo.pt"); parser.add_argument("--conf", type=float, default=.35)
args = parser.parse_args()
print(FireguardRuntime(args.weights).predict(Image.open(Path(args.source)).convert("RGB"), args.conf))
