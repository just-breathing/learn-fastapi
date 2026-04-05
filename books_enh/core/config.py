from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings: AppSettings = AppSettings() # type: ignore