from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient


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


def test_spotify_callback(client: TestClient) -> None:
    response = client.get(
        "/auth/spotify/callback",
        params={
            "code": "spotify-code",
            "state": "state-value",
            "expected_state": "state-value",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"code": "spotify-code", "state": "state-value"}


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
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Spotify state"}
