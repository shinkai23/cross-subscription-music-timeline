from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.spotify_auth_schema import (
    SpotifyAuthorizationResponse,
    SpotifyCallbackResponse,
)
from app.services.spotify_auth_service import (
    InvalidSpotifyStateError,
    SpotifyTokenExchangeError,
    build_spotify_authorization_request,
    exchange_spotify_code_for_token,
    validate_spotify_callback_state,
)

router = APIRouter(prefix="/auth/spotify", tags=["spotify-auth"])


@router.get("/authorize", response_model=SpotifyAuthorizationResponse)
def authorize_spotify() -> SpotifyAuthorizationResponse:
    authorization_request = build_spotify_authorization_request()

    return SpotifyAuthorizationResponse(
        authorization_url=authorization_request.authorization_url,
        state=authorization_request.state,
        code_verifier=authorization_request.code_verifier,
    )


@router.get("/callback", response_model=SpotifyCallbackResponse)
async def spotify_callback(
    code: str = Query(...),
    state: str = Query(...),
    expected_state: str = Query(...),
    code_verifier: str = Query(...),
) -> SpotifyCallbackResponse:
    try:
        validate_spotify_callback_state(
            expected_state=expected_state,
            actual_state=state,
        )
        token_response = await exchange_spotify_code_for_token(
            code=code,
            code_verifier=code_verifier,
        )
    except InvalidSpotifyStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Spotify state",
        ) from exc
    except SpotifyTokenExchangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange Spotify code",
        ) from exc

    return SpotifyCallbackResponse.model_validate(token_response.model_dump())
