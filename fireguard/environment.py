from __future__ import annotations
import logging
from datetime import datetime,timezone
import httpx
logger=logging.getLogger(__name__)
class EnvironmentalProvider:
    name="UNAVAILABLE"
    async def current(self,latitude=None,longitude=None): raise NotImplementedError
def base(latitude,longitude):
    return {"temperature":None,"humidity":None,"wind_speed":None,"wind_direction":None,"rainfall":None,"pressure":None,"pm25":None,"pm10":None,"visibility":None,"source":"UNAVAILABLE","timestamp":datetime.now(timezone.utc).isoformat(),"demo":False,"freshness":"UNAVAILABLE","status":"UNAVAILABLE","location_available":latitude is not None and longitude is not None}
class UnavailableProvider(EnvironmentalProvider):
    async def current(self,latitude=None,longitude=None): p=base(latitude,longitude); p["message"]="No environmental provider is configured."; return p
class DemoProvider(EnvironmentalProvider):
    name="DEMO"
    async def current(self,latitude=None,longitude=None): return {"temperature":32.5,"humidity":31.0,"wind_speed":24.0,"wind_direction":210.0,"rainfall":0.0,"pressure":1012.0,"pm25":18.5,"pm10":25.0,"visibility":8.5,"source":"DEMO","timestamp":datetime.now(timezone.utc).isoformat(),"demo":True,"freshness":"DEMO","status":"DEMO_MODE","message":"Demo data is active. This is not live monitoring data.","location_available":latitude is not None and longitude is not None}
class OpenMeteoProvider(EnvironmentalProvider):
    name="OPEN_METEO"
    def __init__(self,url,timeout_seconds=10): self.url=url; self.timeout=httpx.Timeout(timeout_seconds)
    async def current(self,latitude=None,longitude=None):
        if latitude is None or longitude is None: p=base(latitude,longitude); p["source"]=self.name; p["message"]="Configure FIREGUARD_LATITUDE and FIREGUARD_LONGITUDE for live weather."; return p
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r=await c.get(self.url,params={"latitude":latitude,"longitude":longitude,"current":"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,surface_pressure","timezone":"UTC"}); r.raise_for_status(); d=r.json()
            cur=d.get("current",{}); t=cur.get("time")
            if not t: raise ValueError("missing observation time")
            return {"temperature":cur.get("temperature_2m"),"humidity":cur.get("relative_humidity_2m"),"wind_speed":cur.get("wind_speed_10m"),"wind_direction":cur.get("wind_direction_10m"),"rainfall":cur.get("precipitation"),"pressure":cur.get("surface_pressure"),"pm25":None,"pm10":None,"visibility":None,"source":self.name,"timestamp":t,"demo":False,"freshness":"LIVE","status":"LIVE","location_available":True,"units":d.get("current_units",{})}
        except Exception as e:
            logger.warning("weather failed: %s",e); p=base(latitude,longitude); p["source"]=self.name; p["message"]=f"Live weather unavailable: {e.__class__.__name__}"; return p
class WeatherAPIProvider(OpenMeteoProvider): name="OPEN_METEO"
class SensorProvider(UnavailableProvider): name="SENSOR_PROVIDER"
class CSVProvider(UnavailableProvider): name="CSV_PROVIDER"
class IoTSensorProvider(UnavailableProvider): name="IOT_SENSOR_PROVIDER"
class AirQualityProvider(UnavailableProvider): name="AIR_QUALITY_PROVIDER"
