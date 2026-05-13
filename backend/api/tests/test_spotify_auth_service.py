from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app.core.config import get_settings
from app.services.spotify_auth_service import (
    InvalidSpotifyStateError,
    SPOTIFY_AUTHORIZE_URL,
    SPOTIFY_ME_URL,
    SPOTIFY_TOKEN_URL,
    SpotifyCurrentUserFetchError,
    SpotifyTokenExchangeError,
    build_code_challenge,
    build_spotify_authorization_request,
    build_spotify_authorization_url,
    build_spotify_token_exchange_payload,
    exchange_spotify_code_for_token,
    fetch_spotify_current_user_id,
    generate_code_verifier,
    validate_spotify_callback_state,
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


def test_validate_spotify_callback_state_accepts_matching_state() -> None:
    validate_spotify_callback_state(
        expected_state="state-value",
        actual_state="state-value",
    )


def test_validate_spotify_callback_state_rejects_mismatched_state() -> None:
    with pytest.raises(InvalidSpotifyStateError):
        validate_spotify_callback_state(
            expected_state="expected-state",
            actual_state="actual-state",
        )


def test_build_spotify_token_exchange_payload() -> None:
    settings = get_settings()

    payload = build_spotify_token_exchange_payload(
        code="spotify-code",
        code_verifier="code-verifier",
    )

    assert payload == {
        "grant_type": "authorization_code",
        "code": "spotify-code",
        "redirect_uri": settings.spotify_redirect_uri,
        "client_id": settings.spotify_client_id,
        "code_verifier": "code-verifier",
    }


@pytest.mark.anyio
async def test_exchange_spotify_code_for_token() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == SPOTIFY_TOKEN_URL
        assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert b"grant_type=authorization_code" in request.content
        assert b"code=spotify-code" in request.content
        assert b"code_verifier=code-verifier" in request.content

        return httpx.Response(
            status_code=200,
            json={
                "access_token": "access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh-token",
                "scope": "playlist-read-private",
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        token_response = await exchange_spotify_code_for_token(
            code="spotify-code",
            code_verifier="code-verifier",
            client=client,
        )

    assert token_response.access_token == "access-token"
    assert token_response.token_type == "Bearer"
    assert token_response.expires_in == 3600
    assert token_response.refresh_token == "refresh-token"
    assert token_response.scope == "playlist-read-private"


@pytest.mark.anyio
async def test_exchange_spotify_code_for_token_raises_on_error() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=400, json={"error": "invalid_grant"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(SpotifyTokenExchangeError):
            await exchange_spotify_code_for_token(
                code="spotify-code",
                code_verifier="code-verifier",
                client=client,
            )


@pytest.mark.anyio
async def test_fetch_spotify_current_user_id() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == SPOTIFY_ME_URL
        assert request.headers["Authorization"] == "Bearer access-token"
        return httpx.Response(status_code=200, json={"id": "spotify-user-1"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider_user_id = await fetch_spotify_current_user_id(
            access_token="access-token",
            client=client,
        )

    assert provider_user_id == "spotify-user-1"


@pytest.mark.anyio
async def test_fetch_spotify_current_user_id_raises_on_error() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=401, json={"error": "invalid_token"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(SpotifyCurrentUserFetchError):
            await fetch_spotify_current_user_id(
                access_token="access-token",
                client=client,
            )
