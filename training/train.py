from pathlib import Path
import argparse, yaml

def main():
 p=argparse.ArgumentParser(); p.add_argument('--data',default='data/processed'); p.add_argument('--model',default='yolo11n.pt'); p.add_argument('--epochs',type=int,default=50); p.add_argument('--batch',type=int,default=16); p.add_argument('--resume',action='store_true'); a=p.parse_args()
 try:
  from ultralytics import YOLO
 except ImportError: raise SystemExit("Install ML dependencies with: pip install -e '.[ml]'")
 root=Path(a.data); names={}
 for f in root.rglob('*.txt'):
  for line in f.read_text(errors='ignore').splitlines():
   if line.strip(): names.setdefault(int(line.split()[0]),f'class_{line.split()[0]}')
 cfg={'path':str(root.resolve()),'train':'train','val':'val','test':'test','names':names}
 (root/'dataset.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False)); model=YOLO(a.model); model.train(data=str(root/'dataset.yaml'),epochs=a.epochs,batch=a.batch,device=0 if __import__('utils.device',fromlist=['detect_device']).detect_device()=='cuda' else 'cpu',resume=a.resume,project='runs/train')
if __name__=='__main__': main()
