from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .environment import DemoProvider
from .risk import calculate_risk
from utils.device import get_gpu_info,get_gpu_memory,get_gpu_utilization
app=FastAPI(title='FIREGUARD AI',version='0.1.0'); app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(','),allow_methods=['*'],allow_headers=['*'])
environment=DemoProvider()
@app.get('/api/health')
async def health(): return {'status':'ok','demo_mode':settings.demo_mode}
@app.get('/api/system/gpu')
def gpu(): return {'info':get_gpu_info(),'memory':get_gpu_memory(),'utilization':get_gpu_utilization()}
@app.get('/api/environment/current')
async def env(): return await environment.current()
@app.get('/api/risk/{event_id}')
def risk(event_id:str): return {'event_id':event_id,**calculate_risk({})}
@app.get('/api/fires')
def fires(): return []
@app.get('/api/alerts')
def alerts(): return []
@app.get('/api/model/status')
def model_status(): return {'weights_configured':bool(settings.model_weights),'metrics_available':False}
@app.get('/api/dataset/statistics')
def dataset_statistics():
 from pathlib import Path
 import json
 p=Path('reports/dataset_report.json'); return json.loads(p.read_text()) if p.exists() else {'status':'NOT_INSPECTED'}
@app.post('/api/detection/image')
async def detect_image(file:UploadFile=File(...)): return {'status':'queued','filename':file.filename,'metrics_available':False}
@app.websocket('/ws/live')
async def live(ws:WebSocket):
 await ws.accept(); await ws.send_json({'type':'status','message':'Connected; awaiting real source data'}); await ws.close()
