def main():
 import argparse, json
 from ultralytics import YOLO
 p=argparse.ArgumentParser(); p.add_argument('--weights',required=True); p.add_argument('--data',required=True); p.add_argument('--split',default='test'); a=p.parse_args(); r=YOLO(a.weights).val(data=a.data,split=a.split,plots=True); print(json.dumps({'precision':float(r.box.mp),'recall':float(r.box.mr),'map50':float(r.box.map50),'map50_95':float(r.box.map)},indent=2))
if __name__=='__main__': main()
