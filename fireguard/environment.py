from datetime import datetime, timezone
from typing import Any
class EnvironmentalProvider:
 async def current(self,latitude:float|None=None,longitude:float|None=None)->dict[str,Any]: raise NotImplementedError
class DemoProvider(EnvironmentalProvider):
 async def current(self,**kwargs): return {'demo':True,'source':'DEMO DATA','timestamp':datetime.now(timezone.utc).isoformat()}
class CSVProvider(EnvironmentalProvider):
 def __init__(self,path): self.path=path
 async def current(self,**kwargs):
  import csv
  with open(self.path,newline='') as f: return {**next(csv.DictReader(f)),'source':'CSV','demo':False}
