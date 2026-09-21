from __future__ import annotations
import logging
from datetime import datetime,timezone
from typing import Any
import httpx
from fireguard.config import settings
log=logging.getLogger(__name__)
def ts(): return datetime.now(timezone.utc).isoformat()
async def fetch_air_quality(lat:float,lon:float):
    try:
        async with httpx.AsyncClient(timeout=settings.environment_timeout_seconds) as c:
            r=await c.get(settings.air_quality_api_url,params={"latitude":lat,"longitude":lon,"current":"pm10,pm2_5,carbon_monoxide,nitrogen_dioxide","timezone":"UTC"}); r.raise_for_status(); cur=r.json().get("current",{})
        return {"pm25":cur.get("pm2_5"),"pm10":cur.get("pm10"),"air_quality_status":"LIVE","air_quality_source":"OPEN_METEO_AIR_QUALITY","air_quality_timestamp":cur.get("time") or ts()}
    except Exception as e:
        log.warning("air quality failed: %s",e); return {"pm25":None,"pm10":None,"air_quality_status":"UNAVAILABLE","air_quality_source":"OPEN_METEO_AIR_QUALITY","air_quality_timestamp":ts()}
async def fetch_elevation(lat:float,lon:float):
    try:
        async with httpx.AsyncClient(timeout=settings.environment_timeout_seconds) as c:
            r=await c.get(settings.elevation_api_url,params={"latitude":lat,"longitude":lon}); r.raise_for_status(); e=r.json().get("elevation",[])
        return {"elevation_m":e[0] if e else None,"terrain_status":"LIVE" if e else "UNAVAILABLE","terrain_source":"OPEN_METEO_ELEVATION","terrain_timestamp":ts()}
    except Exception as e:
        log.warning("elevation failed: %s",e); return {"elevation_m":None,"terrain_status":"UNAVAILABLE","terrain_source":"OPEN_METEO_ELEVATION","terrain_timestamp":ts()}
async def fetch_firms(lat=None,lon=None):
    if not settings.firms_map_key: return {"fires":[],"satellite_status":"CONFIG_REQUIRED","satellite_source":"NASA_FIRMS","satellite_message":"Set FIREGUARD_FIRMS_MAP_KEY.","satellite_timestamp":ts()}
    url=f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{settings.firms_map_key}/{settings.firms_source}/{settings.firms_region}/{settings.firms_days}"
    try:
        async with httpx.AsyncClient(timeout=settings.environment_timeout_seconds) as c: r=await c.get(url); r.raise_for_status(); raw=r.text
        lines=[x.strip() for x in raw.splitlines() if x.strip()]; fires=[]
        if len(lines)>1:
            head=[x.strip() for x in lines[0].split(",")]
            for line in lines[1:]:
                vals=line.split(",")
                if len(vals)<len(head): continue
                row=dict(zip(head,vals))
                try: la=float(row["latitude"]); lo=float(row["longitude"])
                except (KeyError,ValueError): continue
                if lat is not None and lon is not None and (abs(la-lat)>5 or abs(lo-lon)>5): continue
                fires.append({"event_id":f"firms-{row.get('acq_date')}-{row.get('acq_time')}-{la:.4f}-{lo:.4f}","latitude":la,"longitude":lo,"confidence":row.get("confidence"),"frp":row.get("frp"),"satellite":row.get("satellite"),"instrument":row.get("instrument"),"acq_date":row.get("acq_date"),"acq_time":row.get("acq_time"),"source":"NASA_FIRMS","status":"SATELLITE_OBSERVATION"})
        return {"fires":fires,"satellite_status":"LIVE","satellite_source":"NASA_FIRMS","satellite_timestamp":ts()}
    except Exception as e:
        log.warning("FIRMS failed: %s",e); return {"fires":[],"satellite_status":"UNAVAILABLE","satellite_source":"NASA_FIRMS","satellite_timestamp":ts()}
async def collect_live_sources(lat,lon):
    result={"timestamp":ts(),"satellite":await fetch_firms(lat,lon)}
    if lat is not None and lon is not None:
        result["air_quality"]=await fetch_air_quality(lat,lon); result["terrain"]=await fetch_elevation(lat,lon)
    return result
