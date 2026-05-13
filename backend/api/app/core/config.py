from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cross-Subscription Music Timeline API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://music:music@localhost:5432/music_timeline"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    spotify_client_id: str = ""
    spotify_redirect_uri: str = "http://localhost:4000/auth/spotify/callback"
    spotify_auth_scopes: str = (
        "playlist-read-private "
        "playlist-modify-private "
        "playlist-modify-public"
    )
    token_encryption_key: str = "3QUlaYLveO5FK5fWDYTA7O7um9OzDCV4u2NA-ZXq9a0="

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
