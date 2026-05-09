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
