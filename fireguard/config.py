from pydantic_settings import BaseSettings
class Settings(BaseSettings):
 demo_mode:bool=False; database_url:str='sqlite:///./fireguard.db'; model_weights:str|None=None; cors_origins:str='http://localhost:5173'; confidence_threshold:float=.35; temporal_window:int=12; minimum_persistence:int=3
 class Config: env_file='.env'; env_prefix='FIREGUARD_'
settings=Settings()
