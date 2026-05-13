from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.service_account import ServiceAccount
from app.models.user import User
from app.schemas.spotify_auth_schema import SpotifyTokenResponse


def test_authorize_spotify(client: TestClient) -> None:
    response = client.get("/auth/spotify/authorize")

    assert response.status_code == 200
    body = response.json()
    assert body["authorization_url"]
    assert body["state"]
    assert body["code_verifier"]

    parsed_url = urlparse(body["authorization_url"])
    query = parse_qs(parsed_url.query, keep_blank_values=True)

    assert query["state"] == [body["state"]]
    assert query["code_challenge_method"] == ["S256"]


def test_spotify_callback(client: TestClient, monkeypatch) -> None:
    async def fake_exchange_spotify_code_for_token(
        code: str,
        code_verifier: str,
    ) -> SpotifyTokenResponse:
        assert code == "spotify-code"
        assert code_verifier == "code-verifier"
        return SpotifyTokenResponse(
            access_token="access-token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh-token",
            scope="playlist-read-private",
        )

    monkeypatch.setattr(
        "app.routers.spotify_oauth_router.exchange_spotify_code_for_token",
        fake_exchange_spotify_code_for_token,
    )

    response = client.get(
        "/auth/spotify/callback",
        params={
            "code": "spotify-code",
            "state": "state-value",
            "expected_state": "state-value",
            "code_verifier": "code-verifier",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "refresh-token",
        "scope": "playlist-read-private",
    }


def test_spotify_callback_requires_code_and_state(client: TestClient) -> None:
    response = client.get("/auth/spotify/callback")

    assert response.status_code == 422


def test_spotify_callback_rejects_mismatched_state(client: TestClient) -> None:
    response = client.get(
        "/auth/spotify/callback",
        params={
            "code": "spotify-code",
            "state": "actual-state",
            "expected_state": "expected-state",
            "code_verifier": "code-verifier",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Spotify state"}


def test_spotify_callback_returns_502_when_token_exchange_fails(
    client: TestClient,
    monkeypatch,
) -> None:
    from app.services.spotify_auth_service import SpotifyTokenExchangeError

    async def fake_exchange_spotify_code_for_token(
        code: str,
        code_verifier: str,
    ) -> SpotifyTokenResponse:
        raise SpotifyTokenExchangeError()

    monkeypatch.setattr(
        "app.routers.spotify_oauth_router.exchange_spotify_code_for_token",
        fake_exchange_spotify_code_for_token,
    )

    response = client.get(
        "/auth/spotify/callback",
        params={
            "code": "spotify-code",
            "state": "state-value",
            "expected_state": "state-value",
            "code_verifier": "code-verifier",
        },
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "Failed to exchange Spotify code"}


def test_connect_spotify(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    async def fake_exchange_spotify_code_for_token(
        code: str,
        code_verifier: str,
    ) -> SpotifyTokenResponse:
        assert code == "spotify-code"
        assert code_verifier == "code-verifier"
        return SpotifyTokenResponse(
            access_token="access-token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh-token",
            scope="playlist-read-private",
        )

    async def fake_fetch_spotify_current_user_id(access_token: str) -> str:
        assert access_token == "access-token"
        return "spotify-user-1"

    monkeypatch.setattr(
        "app.routers.spotify_oauth_router.exchange_spotify_code_for_token",
        fake_exchange_spotify_code_for_token,
    )
    monkeypatch.setattr(
        "app.routers.spotify_oauth_router.fetch_spotify_current_user_id",
        fake_fetch_spotify_current_user_id,
    )

    response = client.post(
        "/auth/spotify/connect",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "spotify-code",
            "code_verifier": "code-verifier",
            "state": "state-value",
            "expected_state": "state-value",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "spotify",
        "provider_user_id": "spotify-user-1",
    }

    service_account = db_session.query(ServiceAccount).one()
    assert service_account.user_id == user.id
    assert service_account.provider == "spotify"
    assert service_account.provider_user_id == "spotify-user-1"
    assert service_account.encrypted_refresh_token == "refresh-token"
    assert service_account.scopes == "playlist-read-private"


def test_connect_spotify_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/auth/spotify/connect",
        json={
            "code": "spotify-code",
            "code_verifier": "code-verifier",
            "state": "state-value",
            "expected_state": "state-value",
        },
    )

    assert response.status_code == 401


def test_connect_spotify_returns_409_when_account_is_already_connected(
    client: TestClient,
    db_session: Session,
    monkeypatch,
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
            provider="spotify",
            provider_user_id="spotify-user-1",
        )
    )
    db_session.commit()
    token = create_access_token(subject=current_user.id)

    async def fake_exchange_spotify_code_for_token(
        code: str,
        code_verifier: str,
    ) -> SpotifyTokenResponse:
        return SpotifyTokenResponse(
            access_token="access-token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh-token",
            scope="playlist-read-private",
        )

    async def fake_fetch_spotify_current_user_id(access_token: str) -> str:
        return "spotify-user-1"

    monkeypatch.setattr(
        "app.routers.spotify_oauth_router.exchange_spotify_code_for_token",
        fake_exchange_spotify_code_for_token,
    )
    monkeypatch.setattr(
        "app.routers.spotify_oauth_router.fetch_spotify_current_user_id",
        fake_fetch_spotify_current_user_id,
    )

    response = client.post(
        "/auth/spotify/connect",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "spotify-code",
            "code_verifier": "code-verifier",
            "state": "state-value",
            "expected_state": "state-value",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Spotify account is already connected"}
