from fastapi import FastAPI

from app.core.exceptions import provider_api_error_handler
from app.providers.error import ProviderApiError
from app.routers.apple_music_auth_router import router as apple_music_auth_router
from app.routers.health_router import router as health_router
from app.routers.post_router import router as post_router
from app.routers.provider_router import router as provider_router
from app.routers.spotify_oauth_router import router as spotify_auth_router
from app.routers.user_router import router as user_router

app = FastAPI(title="Cross-Subscription Music Timeline API")
app.include_router(health_router)
app.include_router(post_router)
app.include_router(user_router)
app.include_router(spotify_auth_router)
app.include_router(apple_music_auth_router)
app.include_router(provider_router)

app.add_exception_handler(ProviderApiError, provider_api_error_handler)
