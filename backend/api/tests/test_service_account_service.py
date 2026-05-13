import pytest
from sqlalchemy.orm import Session

from app.models.service_account import ServiceAccount
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.spotify_auth_schema import SpotifyTokenResponse
from app.services.service_account_service import (
    ServiceAccountAlreadyConnectedError,
    ServiceAccountService,
)
from app.services.token_encryption_service import TokenEncryptionService


class FakeTokenEncryptionService(TokenEncryptionService):
    def encrypt(self, token: str | None) -> str | None:
        if token is None:
            return None
        return f"encrypted:{token}"


def test_connect_spotify_account_creates_service_account(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    token_response = SpotifyTokenResponse(
        access_token="access-token",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="refresh-token",
        scope="playlist-read-private playlist-modify-private",
    )

    service_account = service.connect_spotify_account(
        user=user,
        provider_user_id="spotify-user-1",
        token_response=token_response,
    )

    assert service_account.user_id == user.id
    assert service_account.provider == "spotify"
    assert service_account.provider_user_id == "spotify-user-1"
    assert service_account.encrypted_refresh_token == "encrypted:refresh-token"
    assert service_account.scopes == "playlist-read-private playlist-modify-private"


def test_connect_spotify_account_returns_existing_account_for_same_user(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, TokenEncryptionService())
    token_response = SpotifyTokenResponse(
        access_token="access-token",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="refresh-token",
        scope="playlist-read-private",
    )
    existing_service_account = repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
        encrypted_refresh_token="existing-refresh-token",
        scopes="existing-scope",
    )

    service_account = service.connect_spotify_account(
        user=user,
        provider_user_id="spotify-user-1",
        token_response=token_response,
    )

    assert service_account.id == existing_service_account.id
    assert db_session.query(ServiceAccount).count() == 1


def test_connect_spotify_account_rejects_account_connected_to_other_user(
    db_session: Session,
) -> None:
    connected_user = User(display_name="Connected User", handle="connected-user")
    current_user = User(display_name="Current User", handle="current-user")
    db_session.add_all([connected_user, current_user])
    db_session.commit()
    db_session.refresh(connected_user)
    db_session.refresh(current_user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, TokenEncryptionService())
    repository.create_service_account(
        user_id=connected_user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
    )
    token_response = SpotifyTokenResponse(
        access_token="access-token",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="refresh-token",
        scope="playlist-read-private",
    )

    with pytest.raises(ServiceAccountAlreadyConnectedError):
        service.connect_spotify_account(
            user=current_user,
            provider_user_id="spotify-user-1",
            token_response=token_response,
        )
