import pytest
from sqlalchemy.orm import Session

from app.models.service_account import ServiceAccount
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.spotify_auth_schema import SpotifyTokenResponse
from app.services.service_account_errors import (
    ServiceAccountAlreadyConnectedError,
    ServiceAccountNotConnectedError,
    ServiceAccountRefreshTokenMissingError,
)
from app.services.service_account_service import (
    ServiceAccountService,
)
from app.services.token_encryption_service import TokenEncryptionService


class FakeTokenEncryptionService(TokenEncryptionService):
    def encrypt(self, token: str | None) -> str | None:
        if token is None:
            return None
        return f"encrypted:{token}"

    def decrypt(self, encrypted_token: str | None) -> str | None:
        if encrypted_token is None:
            return None
        return encrypted_token.removeprefix("encrypted:")


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


def test_connect_apple_music_account_creates_service_account(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())

    service_account = service.connect_apple_music_account(
        user=user,
        provider_user_id="apple-user-1",
        music_user_token="music-user-token",
    )

    assert service_account.user_id == user.id
    assert service_account.provider == "apple_music"
    assert service_account.provider_user_id == "apple-user-1"
    assert service_account.encrypted_refresh_token == "encrypted:music-user-token"
    assert service_account.scopes is None


def test_connect_apple_music_account_returns_existing_account_for_same_user(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    existing_service_account = repository.create_service_account(
        user_id=user.id,
        provider="apple_music",
        provider_user_id="apple-user-1",
        encrypted_refresh_token="existing-music-user-token",
    )

    service_account = service.connect_apple_music_account(
        user=user,
        provider_user_id="apple-user-1",
        music_user_token="music-user-token",
    )

    assert service_account.id == existing_service_account.id
    assert db_session.query(ServiceAccount).count() == 1


def test_connect_apple_music_account_rejects_account_connected_to_other_user(
    db_session: Session,
) -> None:
    connected_user = User(display_name="Connected User", handle="connected-user")
    current_user = User(display_name="Current User", handle="current-user")
    db_session.add_all([connected_user, current_user])
    db_session.commit()
    db_session.refresh(connected_user)
    db_session.refresh(current_user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    repository.create_service_account(
        user_id=connected_user.id,
        provider="apple_music",
        provider_user_id="apple-user-1",
    )

    with pytest.raises(ServiceAccountAlreadyConnectedError):
        service.connect_apple_music_account(
            user=current_user,
            provider_user_id="apple-user-1",
            music_user_token="music-user-token",
        )


@pytest.mark.anyio
async def test_refresh_spotify_access_token_for_account(
    db_session: Session,
    monkeypatch,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
        encrypted_refresh_token="encrypted:refresh-token",
    )

    async def fake_refresh_spotify_access_token(
        refresh_token: str,
    ) -> SpotifyTokenResponse:
        assert refresh_token == "refresh-token"
        return SpotifyTokenResponse(
            access_token="new-access-token",
            token_type="Bearer",
            expires_in=3600,
            scope="playlist-read-private",
        )

    monkeypatch.setattr(
        "app.services.provider_token.spotify_token_service.refresh_spotify_access_token",
        fake_refresh_spotify_access_token,
    )

    access_token = await service.get_provider_access_token(
        user=user,
        provider="spotify",
    )

    assert access_token == "new-access-token"


@pytest.mark.anyio
async def test_refresh_spotify_access_token_for_account_rejects_missing_token(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
        encrypted_refresh_token=None,
    )

    with pytest.raises(ServiceAccountRefreshTokenMissingError):
        await service.get_provider_access_token(
            user=user,
            provider="spotify",
        )


@pytest.mark.anyio
async def test_get_provider_access_token_for_spotify(
    db_session: Session,
    monkeypatch,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
        encrypted_refresh_token="encrypted:refresh-token",
    )

    async def fake_refresh_spotify_access_token(
        refresh_token: str,
    ) -> SpotifyTokenResponse:
        assert refresh_token == "refresh-token"
        return SpotifyTokenResponse(
            access_token="new-access-token",
            token_type="Bearer",
            expires_in=3600,
        )

    monkeypatch.setattr(
        "app.services.provider_token.spotify_token_service.refresh_spotify_access_token",
        fake_refresh_spotify_access_token,
    )

    access_token = await service.get_provider_access_token(
        user=user,
        provider="spotify",
    )

    assert access_token == "new-access-token"


@pytest.mark.anyio
async def test_get_provider_access_token_rejects_not_connected_provider(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())

    with pytest.raises(ServiceAccountNotConnectedError):
        await service.get_provider_access_token(
            user=user,
            provider="spotify",
        )


@pytest.mark.anyio
async def test_get_provider_access_token_for_apple_music(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service = ServiceAccountService(repository, FakeTokenEncryptionService())
    repository.create_service_account(
        user_id=user.id,
        provider="apple_music",
        provider_user_id="apple-user-1",
        encrypted_refresh_token="encrypted:music-user-token",
    )

    access_token = await service.get_provider_access_token(
        user=user,
        provider="apple_music",
    )

    assert access_token == "music-user-token"
