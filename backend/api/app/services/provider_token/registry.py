from app.services.provider_token.apple_music_token_service import AppleMusicTokenService
from app.services.provider_token.base import ProviderTokenService
from app.services.provider_token.spotify_token_service import SpotifyTokenService
from app.services.token_encryption_service import TokenEncryptionService


def get_provider_token_service(
    provider: str,
    token_encryption_service: TokenEncryptionService,
) -> ProviderTokenService:
    if provider == "spotify":
        return SpotifyTokenService(
            token_encryption_service=token_encryption_service,
        )

    if provider == "apple_music":
        return AppleMusicTokenService(
            token_encryption_service=token_encryption_service,
        )

    raise ValueError(f"Unsupported provider: {provider}")
