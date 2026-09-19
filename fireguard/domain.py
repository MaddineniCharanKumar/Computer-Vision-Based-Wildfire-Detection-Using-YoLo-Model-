from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class EventStatus(str,Enum): DETECTED='DETECTED'; CONFIRMED='CONFIRMED'; ACTIVE='ACTIVE'; GROWING='GROWING'; STABLE='STABLE'; REDUCING='REDUCING'; RESOLVED='RESOLVED'
@dataclass
class Detection: confidence:float; bbox:tuple[float,float,float,float]; timestamp:datetime=field(default_factory=lambda:datetime.now(timezone.utc))
@dataclass
class FireEvent:
 event_id:str; camera_id:str; source_type:str; status:EventStatus=EventStatus.DETECTED; detections:list[Detection]=field(default_factory=list); risk_score:float=0; growth_rate:float=0; spread_direction:str='UNKNOWN'; model_version:str='unknown'
 def explain(self,environment=None):
  d=self.detections[-1] if self.detections else None; return {'detection_evidence':f'confidence {d.confidence:.1%}' if d else 'no detection evidence','temporal_evidence':f'{len(self.detections)} observations','growth_evidence':f'area proxy growth {self.growth_rate:.1f}%', 'environmental_evidence':environment or 'not available','risk_evidence':f'risk {self.risk_score:.0f}/100'}

def area_proxy(box): return max(0.0,box[2])*max(0.0,box[3])
def growth_rate(previous,current): return 0.0 if previous<=0 else (current-previous)/previous*100
