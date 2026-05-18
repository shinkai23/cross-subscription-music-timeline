from app.providers.base import (
    CreatePlaylistInput,
    ProviderPlaybackMetadata,
    ProviderPlaylist,
    ProviderTrack,
)
from app.providers.registry import get_provider_adapter
from app.repositories.provider_track_repository import ProviderTrackRepository
from app.repositories.track_repository import TrackRepository


class ProviderService:
    def __init__(
        self,
        track_repository: TrackRepository | None = None,
        provider_track_repository: ProviderTrackRepository | None = None,
    ) -> None:
        self.track_repository = track_repository
        self.provider_track_repository = provider_track_repository

    async def search_tracks(
        self,
        provider: str,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        adapter = get_provider_adapter(provider)
        return await adapter.search_tracks(
            query=query,
            user_token=user_token,
        )

    async def get_playlist(
        self,
        provider: str,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        adapter = get_provider_adapter(provider)
        return await adapter.get_playlist(
            playlist_id=playlist_id,
            user_token=user_token,
        )

    async def create_playlist(
        self,
        provider: str,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        adapter = get_provider_adapter(provider)
        return await adapter.create_playlist(
            input_data=input_data,
            user_token=user_token,
        )

    async def add_tracks_to_playlist(
        self,
        provider: str,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        adapter = get_provider_adapter(provider)
        return await adapter.add_tracks_to_playlist(
            playlist_id=playlist_id,
            track_ids=track_ids,
            user_token=user_token,
        )

    async def get_track_playback(
        self,
        provider: str,
        track_id: str,
        user_token: str,
    ) -> ProviderPlaybackMetadata:
        adapter = get_provider_adapter(provider)
        playback = await adapter.get_track_playback(
            track_id=track_id,
            user_token=user_token,
        )

        if (
            self.track_repository is None
            or self.provider_track_repository is None
        ):
            return playback

        existing_provider_track = (
            self.provider_track_repository.get_by_provider_track_id(
                provider=playback.provider,
                provider_track_id=playback.provider_track_id,
            )
        )

        if existing_provider_track is not None:
            self.provider_track_repository.upsert_playback_metadata(
                track_id=existing_provider_track.track_id,
                playback=playback,
            )
            return playback

        track = self.track_repository.get_or_create_from_playback(playback)
        self.provider_track_repository.upsert_playback_metadata(
            track_id=track.id,
            playback=playback,
        )

        return playback
