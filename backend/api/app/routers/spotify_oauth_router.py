from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.spotify_auth_schema import (
    SpotifyAuthorizationResponse,
    SpotifyCallbackResponse,
    SpotifyConnectRequest,
    SpotifyConnectResponse,
)

from app.services.service_account_service import (
    ServiceAccountAlreadyConnectedError,
    ServiceAccountService,
)
from app.services.token_encryption_service import TokenEncryptionService

from app.services.spotify_auth_service import (
    InvalidSpotifyStateError,
    SpotifyTokenExchangeError,
    SpotifyCurrentUserFetchError,
    build_spotify_authorization_request,
    exchange_spotify_code_for_token,
    validate_spotify_callback_state,
    fetch_spotify_current_user_id,
)

router = APIRouter(prefix="/auth/spotify", tags=["spotify-auth"])


def get_service_account_service(
    db: Session = Depends(get_db),
) -> ServiceAccountService:
    return ServiceAccountService(
        repository=ServiceAccountRepository(db),
        token_encryption_service=TokenEncryptionService(),
    )


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


@router.post("/connect", response_model=SpotifyConnectResponse)
async def connect_spotify(
    request: SpotifyConnectRequest,
    current_user: User = Depends(get_current_user),
    service: ServiceAccountService = Depends(get_service_account_service),
) -> SpotifyConnectResponse:
    try:
        validate_spotify_callback_state(
            expected_state=request.expected_state,
            actual_state=request.state,
        )

        token_response = await exchange_spotify_code_for_token(
            code=request.code,
            code_verifier=request.code_verifier,
        )

        provider_user_id = await fetch_spotify_current_user_id(
            access_token=token_response.access_token,
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

    except SpotifyCurrentUserFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch Spotify account",
        ) from exc

    try:
        service_account = service.connect_spotify_account(
            user=current_user,
            provider_user_id=provider_user_id,
            token_response=token_response,
        )
    except ServiceAccountAlreadyConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Spotify account is already connected",
        ) from exc

    return SpotifyConnectResponse(
        provider=service_account.provider,
        provider_user_id=service_account.provider_user_id,
    )
