from pathlib import Path
import argparse, hashlib, json, imghdr, xml.etree.ElementTree as ET
from collections import Counter
from PIL import Image

IMAGE_EXTS={".jpg",".jpeg",".png",".bmp",".tif",".tiff",".webp"}

def parse_yolo(path):
    boxes=[]
    for line_no,line in enumerate(path.read_text(errors="replace").splitlines(),1):
        if not line.strip(): continue
        p=line.split()
        if len(p)!=5: raise ValueError(f"line {line_no}: expected 5 fields")
        c=int(p[0]); vals=list(map(float,p[1:])); boxes.append((c,*vals))
    return boxes

def inspect(root:Path):
    images=[p for p in root.rglob("*") if p.suffix.lower() in IMAGE_EXTS]
    labels=list(root.rglob("*.txt")); xmls=list(root.rglob("*.xml")); jsons=list(root.rglob("*.json"))
    report={"dataset":str(root),"inspected_at":__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),"counts":{"images":len(images),"label_files":len(labels),"xml_files":len(xmls),"json_files":len(jsons)},"annotation_formats":[],"classes":{},"missing_labels":[],"orphan_labels":[],"corrupted_files":[],"invalid_boxes":[],"duplicates":[],"quality":{"status":"PASS","issues":[]}}
    if labels: report["annotation_formats"].append("YOLO")
    if xmls: report["annotation_formats"].append("VOC/XML")
    if jsons: report["annotation_formats"].append("COCO/JSON")
    image_stems={p.with_suffix('').name for p in images}; label_stems={p.with_suffix('').name for p in labels}
    report["missing_labels"]=[str(p) for p in images if p.with_suffix('.txt').exists() is False and p.with_suffix('.xml').exists() is False]
    report["orphan_labels"]=[str(p) for p in labels if p.stem not in image_stems]
    hashes={}
    for p in images+labels:
        try:
            if p in images: Image.open(p).verify()
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            if digest in hashes: report["duplicates"].append({"file":str(p),"same_as":hashes[digest]})
            else: hashes[digest]=str(p)
        except Exception as e: report["corrupted_files"].append({"file":str(p),"error":str(e)})
    for p in labels:
        try:
            for c,x,y,w,h in parse_yolo(p):
                report["classes"][str(c)]=report["classes"].get(str(c),0)+1
                if not (0<=x<=1 and 0<=y<=1 and 0<w<=1 and 0<h<=1 and x-w/2>=0 and x+w/2<=1 and y-h/2>=0 and y+h/2<=1): report["invalid_boxes"].append({"file":str(p),"class":c,"box":[x,y,w,h]})
        except Exception as e: report["quality"]["issues"].append({"file":str(p),"error":str(e)})
    issues=sum(len(report[k]) for k in ("missing_labels","orphan_labels","corrupted_files","invalid_boxes","duplicates"))+len(report["quality"]["issues"])
    report["quality"]={"status":"WARN" if issues else "PASS","issue_count":issues,"issues":report["quality"]["issues"]}
    return report

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',type=Path,required=True); ap.add_argument('--output',type=Path,default=Path('reports')); a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    r=inspect(a.dataset); (a.output/'dataset_report.json').write_text(json.dumps(r,indent=2));
    rows=''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in r['counts'].items())
    (a.output/'dataset_report.html').write_text(f'<html><body><h1>FIREGUARD Dataset Report</h1><p>Status: {r["quality"]["status"]}</p><table>{rows}</table><pre>{json.dumps(r,indent=2)}</pre></body></html>')
    print(json.dumps(r,indent=2))
if __name__=='__main__': main()
