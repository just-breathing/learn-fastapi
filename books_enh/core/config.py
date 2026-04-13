from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class AppSettings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: Optional[str] = None

    STORAGE_URL: str
    STORAGE_ACCOUNT_SECRET: str
    STORAGE_BUCKET_NAME: str
    STORAGE_PRESIGNED_URL_EXPIRY: int = 3600

    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = ["pdf"]
    ALLOWED_MIME_TYPES: list[str] = ["application/pdf"]
    
    DEFAULT_LOAN_DAYS: int = 14
    MAX_LOAN_DAYS: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings: AppSettings = AppSettings() # type - ignore