from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./trinetra.db"
    upload_dir: Path = Path(".data/uploads")
    max_upload_bytes: int = 10 * 1024 * 1024
    log_level: str = "INFO"


settings = Settings()
