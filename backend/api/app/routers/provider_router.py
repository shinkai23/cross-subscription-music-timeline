from fastapi import APIRouter, Depends, Query

from app.providers.base import CreatePlaylistInput, ProviderPlaylist, ProviderTrack
from app.schemas.provider_schema import AddTracksToPlaylistRequest
from app.services.provider_service import ProviderService

router = APIRouter(prefix="/providers", tags=["providers"])


def get_provider_service() -> ProviderService:
    return ProviderService()


@router.get("/{provider}/search/tracks", response_model=list[ProviderTrack])
async def search_tracks(
    provider: str,
    q: str = Query(..., min_length=1),
    user_token: str | None = Query(default=None),
    service: ProviderService = Depends(get_provider_service),
) -> list[ProviderTrack]:
    return await service.search_tracks(
        provider=provider,
        query=q,
        user_token=user_token,
    )


@router.get("/{provider}/playlists/{playlist_id}", response_model=ProviderPlaylist)
async def get_playlist(
    provider: str,
    playlist_id: str,
    user_token: str | None = Query(default=None),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaylist:
    return await service.get_playlist(
        provider=provider,
        playlist_id=playlist_id,
        user_token=user_token,
    )


@router.post("/{provider}/playlists", response_model=ProviderPlaylist)
async def create_playlist(
    provider: str,
    input_data: CreatePlaylistInput,
    user_token: str = Query(..., min_length=1),
    service: ProviderService = Depends(get_provider_service),
) -> ProviderPlaylist:
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
    user_token: str = Query(..., min_length=1),
    service: ProviderService = Depends(get_provider_service),
) -> dict[str, str]:
    await service.add_tracks_to_playlist(
        provider=provider,
        playlist_id=playlist_id,
        track_ids=request.track_ids,
        user_token=user_token,
    )
    return {"status": "ok"}
