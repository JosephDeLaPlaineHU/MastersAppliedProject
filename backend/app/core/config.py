from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Masters Project API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DB: str = "masters_project"
    POSTGRES_PORT: str = "5433"
    DATABASE_URL: Optional[str] = None

    # Security
    SECRET_KEY: str = "SECRET_KEY_SHOULD_CHANGE_THIS_EVENTUALLY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Proxmox
    PROXMOX_URL: str = "https://192.168.1.34:8006"
    PROXMOX_USER: str = "root@pam"
    PROXMOX_PASSWORD: str = "password1!"
    PROXMOX_VERIFY_SSL: bool = False

    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
