from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import (
    CreatePlaylistInput,
    MusicProviderAdapter,
    ProviderPlaybackMetadata,
    ProviderPlaylist,
    ProviderTrack,
)

APPLE_MUSIC_SEARCH_URL = "https://api.music.apple.com/v1/catalog/{storefront}/search"
APPLE_MUSIC_LIBRARY_PLAYLIST_URL = "https://api.music.apple.com/v1/me/library/playlists/{playlist_id}"
APPLE_MUSIC_LIBRARY_PLAYLISTS_URL = "https://api.music.apple.com/v1/me/library/playlists"
APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL = (
    "https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks"
)
APPLE_MUSIC_CATALOG_SONG_URL = (
    "https://api.music.apple.com/v1/catalog/{storefront}/songs/{track_id}"
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

        if response.is_error:
            self._raise_provider_error(response)
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

        if response.is_error:
            self._raise_provider_error(response)
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

        if response.is_error:
            self._raise_provider_error(response)
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

        if response.is_error:
            self._raise_provider_error(response)

    async def get_track_playback(
        self,
        track_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaybackMetadata:
        settings = get_settings()
        if not settings.apple_music_developer_token:
            raise AppleMusicDeveloperTokenRequiredError()

        headers = {"Authorization": f"Bearer {settings.apple_music_developer_token}"}
        if user_token:
            headers["Music-User-Token"] = user_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                APPLE_MUSIC_CATALOG_SONG_URL.format(
                    storefront=settings.apple_music_storefront,
                    track_id=track_id,
                ),
                headers=headers,
            )

        if response.is_error:
            self._raise_provider_error(response)

        data = response.json()["data"][0]
        attributes = data["attributes"]
        play_params = attributes.get("playParams") or {}
        previews = attributes.get("previews") or []

        return ProviderPlaybackMetadata(
            provider=self.provider,
            provider_track_id=data["id"],
            title=attributes["name"],
            artist_name=attributes["artistName"],
            album_name=attributes.get("albumName"),
            duration_ms=attributes.get("durationInMillis"),
            metadata={
                "genre_names": attributes.get("genreNames"),
                "play_params": play_params,
            },
            isrc=attributes.get("isrc"),
            playback_id=play_params.get("id") or data["id"],
            preview_url=previews[0].get("url") if previews else None,
            artwork_url=self._build_artwork_url(attributes.get("artwork")),
            provider_url=attributes.get("url"),
            is_playable=bool(play_params.get("id") or data.get("id")),
        )

    def build_open_url(self, item: Any) -> str:
        provider_id = self._extract_provider_id(item)
        return f"https://music.apple.com/song/{provider_id}"

    def _build_artwork_url(self, artwork: dict[str, Any] | None) -> str | None:
        if artwork is None:
            return None

        url = artwork.get("url")
        if url is None:
            return None

        width = artwork.get("width", 600)
        height = artwork.get("height", 600)
        return url.replace("{w}", str(width)).replace("{h}", str(height))
