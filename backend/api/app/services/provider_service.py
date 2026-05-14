from app.providers.base import CreatePlaylistInput, ProviderPlaylist, ProviderTrack
from app.providers.registry import get_provider_adapter


class ProviderService:
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
