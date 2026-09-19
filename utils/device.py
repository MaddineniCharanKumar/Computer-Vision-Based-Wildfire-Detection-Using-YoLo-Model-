from __future__ import annotations
import subprocess

def detect_device():
 try:
  import torch
  if torch.cuda.is_available(): return 'cuda'
 except ImportError: pass
 return 'cpu'

def get_gpu_info():
 try:
  import torch
  if not torch.cuda.is_available(): return {'available':False,'reason':'CUDA unavailable'}
  return {'available':True,'name':torch.cuda.get_device_name(0),'cuda_version':torch.version.cuda,'device_count':torch.cuda.device_count()}
 except Exception as e: return {'available':False,'reason':str(e)}

def get_gpu_memory():
 try:
  import torch
  if torch.cuda.is_available(): return {'allocated_bytes':torch.cuda.memory_allocated(),'reserved_bytes':torch.cuda.memory_reserved(),'total_bytes':torch.cuda.get_device_properties(0).total_memory}
 except Exception: pass
 return {'available':False}

def get_gpu_utilization():
 try:
  out=subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True,timeout=2).strip().split(',')
  return {'utilization_percent':float(out[0]),'temperature_c':float(out[1])}
 except Exception as e: return {'available':False,'reason':str(e)}

def configure_precision(device=None):
 device=device or detect_device(); return {'device':device,'amp':device=='cuda','half':device=='cuda'}
