from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

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
