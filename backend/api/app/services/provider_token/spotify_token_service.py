from app.models.service_account import ServiceAccount
from app.services.provider_token.base import ProviderTokenService
from app.services.service_account_errors import ServiceAccountRefreshTokenMissingError
from app.services.spotify_auth_service import refresh_spotify_access_token
from app.services.token_encryption_service import TokenEncryptionService


class SpotifyTokenService(ProviderTokenService):
    provider = "spotify"

    def __init__(self, token_encryption_service: TokenEncryptionService) -> None:
        self.token_encryption_service = token_encryption_service

    async def get_access_token(self, service_account: ServiceAccount) -> str:
        refresh_token = self.token_encryption_service.decrypt(
            service_account.encrypted_refresh_token
        )
        if refresh_token is None:
            raise ServiceAccountRefreshTokenMissingError()

        token_response = await refresh_spotify_access_token(refresh_token=refresh_token)
        return token_response.access_token
