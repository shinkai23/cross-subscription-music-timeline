from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository


def test_create_service_account(db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)

    service_account = repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
        encrypted_refresh_token="encrypted-refresh-token",
        scopes="playlist-read-private",
    )

    assert service_account.id
    assert service_account.user_id == user.id
    assert service_account.provider == "spotify"
    assert service_account.provider_user_id == "spotify-user-1"
    assert service_account.encrypted_refresh_token == "encrypted-refresh-token"
    assert service_account.scopes == "playlist-read-private"


def test_get_by_provider_user_id(db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    created_service_account = repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
    )

    found_service_account = repository.get_by_provider_user_id(
        provider="spotify",
        provider_user_id="spotify-user-1",
    )

    assert found_service_account is not None
    assert found_service_account.id == created_service_account.id


def test_get_by_provider_user_id_returns_none_when_missing(
    db_session: Session,
) -> None:
    repository = ServiceAccountRepository(db_session)

    service_account = repository.get_by_provider_user_id(
        provider="spotify",
        provider_user_id="missing-user",
    )

    assert service_account is None


def test_get_by_user_id_and_provider(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    created_service_account = repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
    )

    found_service_account = repository.get_by_user_id_and_provider(
        user_id=user.id,
        provider="spotify",
    )

    assert found_service_account is not None
    assert found_service_account.id == created_service_account.id


def test_get_by_user_id_and_provider_excludes_disconnected_account(
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    repository = ServiceAccountRepository(db_session)
    service_account = repository.create_service_account(
        user_id=user.id,
        provider="spotify",
        provider_user_id="spotify-user-1",
    )
    service_account.disconnected_at = datetime.now(timezone.utc)
    db_session.commit()

    found_service_account = repository.get_by_user_id_and_provider(
        user_id=user.id,
        provider="spotify",
    )

    assert found_service_account is None
