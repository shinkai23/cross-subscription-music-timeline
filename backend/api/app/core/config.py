from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Cross-Subscription Music Timeline API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://music:music@localhost:5432/music_timeline"
    jwt_secret: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")



@lru_cache
def get_settings() -> Settings:
    return Settings()