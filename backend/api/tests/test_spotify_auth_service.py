from urllib.parse import parse_qs, urlparse

from app.core.config import get_settings
from app.services.spotify_auth_service import (
    SPOTIFY_AUTHORIZE_URL,
    build_code_challenge,
    build_spotify_authorization_request,
    build_spotify_authorization_url,
    generate_code_verifier,
)


def test_build_spotify_authorization_url() -> None:
    settings = get_settings()

    authorization_url = build_spotify_authorization_url(
        state="state-value",
        code_challenge="challenge-value",
    )
    parsed_url = urlparse(authorization_url)
    query = parse_qs(parsed_url.query, keep_blank_values=True)

    assert f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}" == (
        SPOTIFY_AUTHORIZE_URL
    )
    assert query["response_type"] == ["code"]
    assert query["client_id"] == [settings.spotify_client_id]
    assert query["redirect_uri"] == [settings.spotify_redirect_uri]
    assert query["scope"] == [settings.spotify_auth_scopes]
    assert query["state"] == ["state-value"]
    assert query["code_challenge"] == ["challenge-value"]
    assert query["code_challenge_method"] == ["S256"]


def test_generate_code_verifier_returns_url_safe_random_value() -> None:
    code_verifier = generate_code_verifier()

    assert len(code_verifier) >= 43
    assert "=" not in code_verifier


def test_build_code_challenge_uses_pkce_s256() -> None:
    code_challenge = build_code_challenge("code-verifier")

    assert code_challenge == "qdgLLRr1saFHT6DWfWU28VNPIi7e9ynEBnBG3Oadw9g"
    assert "=" not in code_challenge


def test_build_spotify_authorization_request() -> None:
    authorization_request = build_spotify_authorization_request()
    parsed_url = urlparse(authorization_request.authorization_url)
    query = parse_qs(parsed_url.query)

    assert authorization_request.state
    assert authorization_request.code_verifier
    assert query["state"] == [authorization_request.state]
    assert query["code_challenge"] == [
        build_code_challenge(authorization_request.code_verifier)
    ]
    assert query["code_challenge_method"] == ["S256"]
