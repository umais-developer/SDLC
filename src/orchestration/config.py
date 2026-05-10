import os
from pydantic_settings import BaseSettings
from typing import Optional

class Config(BaseSettings):
    VAULT_ADDR: str = "http://127.0.0.1:8200"
    VAULT_TOKEN: Optional[str] = None
    
    DB_CONNECTION: str = "postgresql://user:pass@localhost:5432/prescription_db"
    
    GRAPH_TENANT_ID: str = "your-tenant-id"
    GRAPH_CLIENT_ID: str = "your-client-id"
    GRAPH_CLIENT_SECRET: Optional[str] = None
    GRAPH_MAILBOX_ID: str = "rx-intake@yourdomain.com"
    
    DAILY_RUN_TIME: str = "17:00"  # 5 PM
    
    HISTORICAL_LOAD_START_DATE: Optional[str] = None
    
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

config = Config()
