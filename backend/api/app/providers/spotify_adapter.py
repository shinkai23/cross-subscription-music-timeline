from typing import Any

from app.providers.base import (
    CreatePlaylistInput,
    MusicProviderAdapter,
    ProviderPlaylist,
    ProviderTrack,
)


class SpotifyAdapter(MusicProviderAdapter):
    provider = "spotify"

    async def search_tracks(self, query: str, user_token: str | None = None) -> list[ProviderTrack]:
        return []

    async def get_playlist(self, playlist_id: str, user_token: str | None = None) -> ProviderPlaylist:
        return ProviderPlaylist(
            provider=self.provider,
            provider_playlist_id=playlist_id,
            title="",
        )

    async def create_playlist(
        self,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        return ProviderPlaylist(
            provider=self.provider,
            provider_playlist_id="placeholder",
            title=input_data.title,
        )

    async def add_tracks_to_playlist(
        self,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        return None

    def build_open_url(self, item: Any) -> str:
        provider_id = item if isinstance(item, str) else getattr(item, "provider_id", None)
        if provider_id is None and isinstance(item, dict):
            provider_id = item.get("provider_id") or item.get("id")
        return f"https://open.spotify.com/track/{provider_id}"
