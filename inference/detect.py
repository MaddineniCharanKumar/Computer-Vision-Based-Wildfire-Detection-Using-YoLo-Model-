import argparse
from pathlib import Path
from PIL import Image
from fireguard.runtime import FireguardRuntime

p = argparse.ArgumentParser(); p.add_argument("source"); p.add_argument("--weights", default="models/wildfire_yolo.pt"); p.add_argument("--conf", type=float, default=.35)
a = p.parse_args(); result = FireguardRuntime(a.weights).predict(Image.open(Path(a.source)).convert("RGB"), a.conf); print(result)
