from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import (
    CreatePlaylistInput,
    MusicProviderAdapter,
    ProviderPlaylist,
    ProviderTrack,
)

APPLE_MUSIC_SEARCH_URL = "https://api.music.apple.com/v1/catalog/{storefront}/search"
APPLE_MUSIC_LIBRARY_PLAYLIST_URL = "https://api.music.apple.com/v1/me/library/playlists/{playlist_id}"
APPLE_MUSIC_LIBRARY_PLAYLISTS_URL = "https://api.music.apple.com/v1/me/library/playlists"
APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL = (
    "https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks"
)

class AppleMusicDeveloperTokenRequiredError(Exception):
    pass


class AppleMusicUserTokenRequiredError(Exception):
    pass


class AppleMusicAdapter(MusicProviderAdapter):
    provider = "apple_music"

    async def search_tracks(
        self,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        settings = get_settings()
        if not settings.apple_music_developer_token:
            raise AppleMusicDeveloperTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                APPLE_MUSIC_SEARCH_URL.format(
                    storefront=settings.apple_music_storefront
                ),
                params={
                    "term": query,
                    "types": "songs",
                    "limit": 10,
                },
                headers={
                    "Authorization": f"Bearer {settings.apple_music_developer_token}"
                },
            )

        response.raise_for_status()
        data = response.json()

        return [
            ProviderTrack(
                provider=self.provider,
                provider_track_id=item["id"],
                title=item["attributes"]["name"],
                artist_name=item["attributes"]["artistName"],
                album_name=item["attributes"].get("albumName"),
                duration_ms=item["attributes"].get("durationInMillis"),
                isrc=item["attributes"].get("isrc"),
                provider_url=item["attributes"].get("url"),
            )
            for item in data.get("results", {}).get("songs", {}).get("data", [])
        ]

    async def get_playlist(
        self,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        settings = get_settings()
        if not settings.apple_music_developer_token:
            raise AppleMusicDeveloperTokenRequiredError()
        if user_token is None:
            raise AppleMusicUserTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                APPLE_MUSIC_LIBRARY_PLAYLIST_URL.format(playlist_id=playlist_id),
                headers={
                    "Authorization": f"Bearer {settings.apple_music_developer_token}",
                    "Music-User-Token": user_token,
                },
            )

        response.raise_for_status()
        data = response.json()["data"][0]

        return ProviderPlaylist(
            provider=self.provider,
            provider_playlist_id=data["id"],
            title=data["attributes"]["name"],
            provider_url=data["attributes"].get("url"),
        )

    async def create_playlist(
        self,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        settings = get_settings()
        if not settings.apple_music_developer_token:
            raise AppleMusicDeveloperTokenRequiredError()

        if not user_token:
            raise AppleMusicUserTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                APPLE_MUSIC_LIBRARY_PLAYLISTS_URL,
                json={
                    "attributes": {
                        "name": input_data.title,
                        "description": input_data.description or "",
                    }
                },
                headers={
                    "Authorization": f"Bearer {settings.apple_music_developer_token}",
                    "Music-User-Token": user_token,
                },
            )

        response.raise_for_status()
        data = response.json()["data"][0]

        return ProviderPlaylist(
            provider=self.provider,
            provider_playlist_id=data["id"],
            title=data["attributes"]["name"],
            tracks=[],
            provider_url=data["attributes"].get("url"),
        )

    async def add_tracks_to_playlist(
        self,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        settings = get_settings()

        if not settings.apple_music_developer_token:
            raise AppleMusicDeveloperTokenRequiredError()

        if not user_token:
            raise AppleMusicUserTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
                json={
                    "data": [
                        {
                            "id": track_id,
                            "type": "songs",
                        }
                        for track_id in track_ids
                    ]
                },
                headers={
                    "Authorization": f"Bearer {settings.apple_music_developer_token}",
                    "Music-User-Token": user_token,
                },
            )

        response.raise_for_status()

    def build_open_url(self, item: Any) -> str:
        if isinstance(item, str):
            provider_id = item
        elif isinstance(item, dict):
            provider_id = (
                item.get("provider_track_id") or item.get("provider_id") or item.get("id")
            )
        else:
            provider_id = (
                getattr(item, "provider_track_id", None)
                or getattr(item, "provider_id", None)
                or getattr(item, "id", None)
            )

        return f"https://music.apple.com/song/{provider_id}"
