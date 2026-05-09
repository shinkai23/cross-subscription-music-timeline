import base64
import hashlib
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

from app.core.config import get_settings


@dataclass(frozen=True)
class SpotifyAuthorizationRequest:
    authorization_url: str
    state: str
    code_verifier: str


class InvalidSpotifyStateError(Exception):
    pass


SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"


def build_spotify_authorization_url(state: str, code_challenge: str) -> str:
    settings = get_settings()
    query = {
        "response_type": "code",
        "client_id": settings.spotify_client_id,
        "redirect_uri": settings.spotify_redirect_uri,
        "scope": settings.spotify_auth_scopes,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    return f"{SPOTIFY_AUTHORIZE_URL}?{urlencode(query)}"


def generate_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def build_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def build_spotify_authorization_request() -> SpotifyAuthorizationRequest:
    state = secrets.token_urlsafe(32)
    code_verifier = generate_code_verifier()
    code_challenge = build_code_challenge(code_verifier)
    authorization_url = build_spotify_authorization_url(
        state=state,
        code_challenge=code_challenge,
    )

    return SpotifyAuthorizationRequest(
        authorization_url=authorization_url,
        state=state,
        code_verifier=code_verifier,
    )


def validate_spotify_callback_state(expected_state: str, actual_state: str) -> None:
    if expected_state != actual_state:
        raise InvalidSpotifyStateError()
