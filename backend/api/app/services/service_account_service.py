from app.models.service_account import ServiceAccount
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.spotify_auth_schema import SpotifyTokenResponse
from app.services.spotify_auth_service import refresh_spotify_access_token
from app.services.token_encryption_service import TokenEncryptionService


class ServiceAccountAlreadyConnectedError(Exception):
    pass


class ServiceAccountRefreshTokenMissingError(Exception):
    pass


class ServiceAccountNotConnectedError(Exception):
    pass


class ServiceAccountService:
    def __init__(
        self,
        repository: ServiceAccountRepository,
        token_encryption_service: TokenEncryptionService,
    ) -> None:
        self.repository = repository
        self.token_encryption_service = token_encryption_service

    def connect_spotify_account(
        self,
        user: User,
        provider_user_id: str,
        token_response: SpotifyTokenResponse,
    ) -> ServiceAccount:
        existing_service_account = self.repository.get_by_provider_user_id(
            provider="spotify",
            provider_user_id=provider_user_id,
        )
        if existing_service_account is not None:
            if existing_service_account.user_id != user.id:
                raise ServiceAccountAlreadyConnectedError()
            return existing_service_account

        encrypted_refresh_token = self.token_encryption_service.encrypt(
            token_response.refresh_token
        )

        return self.repository.create_service_account(
            user_id=user.id,
            provider="spotify",
            provider_user_id=provider_user_id,
            encrypted_refresh_token=encrypted_refresh_token,
            scopes=token_response.scope,
        )

    async def refresh_spotify_access_token_for_account(
        self,
        service_account: ServiceAccount,
    ) -> SpotifyTokenResponse:
        refresh_token = self.token_encryption_service.decrypt(
            service_account.encrypted_refresh_token
        )

        if refresh_token is None:
            raise ServiceAccountRefreshTokenMissingError()

        return await refresh_spotify_access_token(refresh_token=refresh_token)

    async def get_provider_access_token(
        self,
        user: User,
        provider: str,
    ) -> str:
        service_account = self.repository.get_by_user_id_and_provider(user.id, provider)

        if service_account is None:
            raise ServiceAccountNotConnectedError()

        if provider == "spotify":
            token_response = await self.refresh_spotify_access_token_for_account(
                service_account
            )
            return token_response.access_token
        raise ServiceAccountNotConnectedError()
