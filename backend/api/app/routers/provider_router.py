from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.providers.base import (
    CreatePlaylistInput,
    ProviderPlaylist,
    ProviderTrack,
)
from app.repositories.provider_track_repository import ProviderTrackRepository
from app.repositories.service_account_repository import ServiceAccountRepository
from app.repositories.track_repository import TrackRepository
from app.schemas.provider_schema import AddTracksToPlaylistRequest, ProviderPlaybackRead
from app.services.provider_service import ProviderService
from app.services.service_account_errors import ServiceAccountNotConnectedError
from app.services.service_account_service import ServiceAccountService
from app.services.token_encryption_service import TokenEncryptionService

router = APIRouter(prefix="/providers", tags=["providers"])


@dataclass
class AuthContext:
    provider: str
    user_token: str


def get_provider_service(
    db: Session = Depends(get_db),
) -> ProviderService:
    return ProviderService(
        track_repository=TrackRepository(db),
        provider_track_repository=ProviderTrackRepository(db),
    )


def get_service_account_service(
    db: Session = Depends(get_db),
) -> ServiceAccountService:
    return ServiceAccountService(
        repository=ServiceAccountRepository(db),
        token_encryption_service=TokenEncryptionService(),
    )


async def get_auth_context(
    provider: str,
    current_user: User = Depends(get_current_user),
    service_account_service: ServiceAccountService = Depends(
        get_service_account_service
    ),
) -> AuthContext:
    try:
        user_token = await service_account_service.get_provider_access_token(
            user=current_user,
            provider=provider,
        )
    except ServiceAccountNotConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Provider account is not connected",
        ) from exc

    return AuthContext(
        provider=provider,
        user_token=user_token,
    )


@router.get("/{provider}/search/tracks", response_model=list[ProviderTrack])
async def search_tracks(
    q: str = Query(..., min_length=1),
    auth_context: AuthContext = Depends(get_auth_context),
    service: ProviderService = Depends(get_provider_service),
) -> list[ProviderTrack]:
    return await service.search_tracks(
        provider=auth_context.provider,
        query=q,
        user_token=auth_context.user_token,
    )


@router.get("/{provider}/playlists/{playlist_id}", response_model=ProviderPlaylist)
async def get_playlist(
    playlist_id: str,
    auth_context: AuthContext = Depends(get_auth_context),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaylist:
    return await service.get_playlist(
        provider=auth_context.provider,
        playlist_id=playlist_id,
        user_token=auth_context.user_token,
    )


@router.post("/{provider}/playlists", response_model=ProviderPlaylist)
async def create_playlist(
    input_data: CreatePlaylistInput,
    auth_context: AuthContext = Depends(get_auth_context),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaylist:
    return await service.create_playlist(
        provider=auth_context.provider,
        input_data=input_data,
        user_token=auth_context.user_token,
    )


@router.post("/{provider}/playlists/{playlist_id}/tracks")
async def add_track_to_playlist(
    playlist_id: str,
    request: AddTracksToPlaylistRequest,
    auth_context: AuthContext = Depends(get_auth_context),
    service: ProviderService = Depends(get_provider_service),
) -> dict[str, str]:
    await service.add_tracks_to_playlist(
        provider=auth_context.provider,
        playlist_id=playlist_id,
        track_ids=request.track_ids,
        user_token=auth_context.user_token,
    )
    return {"status": "ok"}


@router.get(
    "/{provider}/tracks/{track_id}/playback",
    response_model=ProviderPlaybackRead,
)
async def get_track_playback(
    track_id: str,
    auth_context: AuthContext = Depends(get_auth_context),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaybackRead:
    return await service.get_track_playback(
        provider=auth_context.provider,
        track_id=track_id,
        user_token=auth_context.user_token,
    )
