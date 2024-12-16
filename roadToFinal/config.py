# BaseSettings: 환경변수 파일 읽어옴
# SettingsConfigDict: 파일 경로 지정
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# 세팅 값을 읽어올 모델
class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    SECRET_ALGORITHM: Optional[str] = None
    EXPIRE_TIMEDELTA: Optional[int]= None
    
    model_config = SettingsConfigDict(env_file='.env')
    
# 인스턴스 생성
settings = Settings()