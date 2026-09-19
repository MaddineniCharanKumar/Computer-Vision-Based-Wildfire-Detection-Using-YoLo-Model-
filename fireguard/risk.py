from dataclasses import dataclass

def risk_level(score):
 return 'LOW' if score<20 else 'GUARDED' if score<40 else 'MODERATE' if score<60 else 'HIGH' if score<80 else 'CRITICAL'
@dataclass
class RiskWeights:
 visual=.25; persistence=.15; growth=.15; wind=.1; temperature=.1; humidity=.1; dryness=.1; smoke=.05

def calculate_risk(features,weights=RiskWeights()):
 score=sum(max(0,min(100,float(features.get(k,0))))*getattr(weights,k) for k in weights.__annotations__)
 return {'score':round(min(100,score),2),'level':risk_level(score),'features':features}
