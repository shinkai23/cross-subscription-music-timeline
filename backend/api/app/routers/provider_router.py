from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.providers.base import CreatePlaylistInput, ProviderPlaylist, ProviderTrack
from app.repositories.service_account_repository import ServiceAccountRepository
from app.schemas.provider_schema import AddTracksToPlaylistRequest
from app.services.provider_service import ProviderService
from app.services.service_account_service import ServiceAccountService
from app.services.token_encryption_service import TokenEncryptionService

router = APIRouter(prefix="/providers", tags=["providers"])


def get_provider_service() -> ProviderService:
    return ProviderService()


def get_service_account_service(
    db: Session = Depends(get_db),
) -> ServiceAccountService:
    return ServiceAccountService(
        repository=ServiceAccountRepository(db),
        token_encryption_service=TokenEncryptionService(),
    )


@router.get("/{provider}/search/tracks", response_model=list[ProviderTrack])
async def search_tracks(
    provider: str,
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    service_account_service: ServiceAccountService = Depends(get_service_account_service),
    service: ProviderService = Depends(get_provider_service),
) -> list[ProviderTrack]:
    user_token = await service_account_service.get_provider_access_token(
        user=current_user,
        provider=provider,
    )
    return await service.search_tracks(
        provider=provider,
        query=q,
        user_token=user_token,
    )


@router.get("/{provider}/playlists/{playlist_id}", response_model=ProviderPlaylist)
async def get_playlist(
    provider: str,
    playlist_id: str,
    current_user: User = Depends(get_current_user),
    service_account_service: ServiceAccountService = Depends(get_service_account_service),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaylist:
    user_token = await service_account_service.get_provider_access_token(
        user=current_user,
        provider=provider,
    )
    return await service.get_playlist(
        provider=provider,
        playlist_id=playlist_id,
        user_token=user_token,
    )


@router.post("/{provider}/playlists", response_model=ProviderPlaylist)
async def create_playlist(
    provider: str,
    input_data: CreatePlaylistInput,
    current_user: User = Depends(get_current_user),
    service_account_service: ServiceAccountService = Depends(get_service_account_service),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaylist:
    user_token = await service_account_service.get_provider_access_token(
        user=current_user,
        provider=provider,
    )
    return await service.create_playlist(
        provider=provider,
        input_data=input_data,
        user_token=user_token,
    )


@router.post("/{provider}/playlists/{playlist_id}/tracks")
async def add_track_to_playlist(
    provider: str,
    playlist_id: str,
    request: AddTracksToPlaylistRequest,
    current_user: User = Depends(get_current_user),
    service_account_service: ServiceAccountService = Depends(get_service_account_service),
    service: ProviderService = Depends(get_provider_service),
) -> dict[str, str]:
    user_token = await service_account_service.get_provider_access_token(
        user=current_user,
        provider=provider,
    )
    await service.add_tracks_to_playlist(
        provider=provider,
        playlist_id=playlist_id,
        track_ids=request.track_ids,
        user_token=user_token,
    )
    return {"status": "ok"}
