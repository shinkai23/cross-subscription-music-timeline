from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.service_account import ServiceAccount
from app.models.user import User
from app.services.token_encryption_service import TokenEncryptionService


def test_connect_apple_music(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    response = client.post(
        "/auth/apple-music/connect",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider_user_id": "apple-user-1",
            "music_user_token": "music-user-token",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "apple_music",
        "connected": True,
    }

    service_account = db_session.query(ServiceAccount).one()
    assert service_account.user_id == user.id
    assert service_account.provider == "apple_music"
    assert service_account.provider_user_id == "apple-user-1"
    assert service_account.encrypted_refresh_token != "music-user-token"
    assert (
        TokenEncryptionService().decrypt(service_account.encrypted_refresh_token)
        == "music-user-token"
    )
    assert service_account.scopes is None


def test_connect_apple_music_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/auth/apple-music/connect",
        json={
            "provider_user_id": "apple-user-1",
            "music_user_token": "music-user-token",
        },
    )

    assert response.status_code == 401


def test_connect_apple_music_requires_body_fields(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    response = client.post(
        "/auth/apple-music/connect",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 422


def test_connect_apple_music_returns_409_when_account_is_already_connected(
    client: TestClient,
    db_session: Session,
) -> None:
    connected_user = User(display_name="Connected User", handle="connected-user")
    current_user = User(display_name="Current User", handle="current-user")
    db_session.add_all([connected_user, current_user])
    db_session.commit()
    db_session.refresh(connected_user)
    db_session.refresh(current_user)
    db_session.add(
        ServiceAccount(
            user_id=connected_user.id,
            provider="apple_music",
            provider_user_id="apple-user-1",
        )
    )
    db_session.commit()
    token = create_access_token(subject=current_user.id)

    response = client.post(
        "/auth/apple-music/connect",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider_user_id": "apple-user-1",
            "music_user_token": "music-user-token",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Apple Music account is already connected"
    }
