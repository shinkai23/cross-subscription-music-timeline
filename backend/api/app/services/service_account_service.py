from app.models.service_account import ServiceAccount
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.spotify_auth_schema import SpotifyTokenResponse
from app.services.provider_token.registry import get_provider_token_service
from app.services.service_account_errors import (
    ServiceAccountAlreadyConnectedError,
    ServiceAccountNotConnectedError,
)
from app.services.token_encryption_service import TokenEncryptionService


class ServiceAccountService:
    def __init__(
        self,
        repository: ServiceAccountRepository,
        token_encryption_service: TokenEncryptionService,
    ) -> None:
        self.repository = repository
        self.token_encryption_service = token_encryption_service

    def connect_provider_account(
        self,
        user: User,
        provider: str,
        provider_user_id: str,
        provider_token: str | None,
        scopes: str | None = None,
    ) -> ServiceAccount:
        existing = self.repository.get_by_provider_user_id(
            provider=provider,
            provider_user_id=provider_user_id,
        )
        if existing is not None:
            if existing.user_id != user.id:
                raise ServiceAccountAlreadyConnectedError()
            return existing

        encrypted_refresh_token = self.token_encryption_service.encrypt(provider_token)

        return self.repository.create_service_account(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            encrypted_refresh_token=encrypted_refresh_token,
            scopes=scopes,
        )

    def connect_spotify_account(
        self,
        user: User,
        provider_user_id: str,
        token_response: SpotifyTokenResponse,
    ) -> ServiceAccount:
        return self.connect_provider_account(
            user=user,
            provider="spotify",
            provider_user_id=provider_user_id,
            provider_token=token_response.refresh_token,
            scopes=token_response.scope,
        )

    def connect_apple_music_account(
        self,
        user: User,
        provider_user_id: str,
        music_user_token: str,
    ) -> ServiceAccount:
        return self.connect_provider_account(
            user=user,
            provider="apple_music",
            provider_user_id=provider_user_id,
            provider_token=music_user_token,
        )

    async def get_provider_access_token(
        self,
        user: User,
        provider: str,
    ) -> str:
        service_account = self.repository.get_by_user_id_and_provider(user.id, provider)

        if service_account is None:
            raise ServiceAccountNotConnectedError()

        token_service = get_provider_token_service(
            provider=provider,
            token_encryption_service=self.token_encryption_service,
        )

        return await token_service.get_access_token(service_account)
