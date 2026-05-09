from fastapi import APIRouter

from app.schemas.spotify_auth_schema import SpotifyAuthorizationResponse
from app.services.spotify_auth_service import build_spotify_authorization_request

router = APIRouter(prefix="/auth/spotify", tags=["spotify-auth"])


@router.get("/authorize", response_model=SpotifyAuthorizationResponse)
def authorize_spotify() -> SpotifyAuthorizationResponse:
    authorization_request = build_spotify_authorization_request()

    return SpotifyAuthorizationResponse(
        authorization_url=authorization_request.authorization_url,
        state=authorization_request.state,
        code_verifier=authorization_request.code_verifier,
    )
