from app.models.service_account import ServiceAccount
from app.services.provider_token.base import ProviderTokenService
from app.services.service_account_errors import ServiceAccountRefreshTokenMissingError
from app.services.token_encryption_service import TokenEncryptionService


class AppleMusicTokenService(ProviderTokenService):
    provider = "apple_music"

    def __init__(self, token_encryption_service: TokenEncryptionService) -> None:
        self.token_encryption_service = token_encryption_service

    async def get_access_token(self, service_account: ServiceAccount) -> str:
        music_user_token = self.token_encryption_service.decrypt(
            service_account.encrypted_refresh_token
        )
        if music_user_token is None:
            raise ServiceAccountRefreshTokenMissingError()

        return music_user_token
