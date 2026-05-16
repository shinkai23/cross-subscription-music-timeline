from typing import Any

import httpx

from app.providers.base import (
    CreatePlaylistInput,
    MusicProviderAdapter,
    ProviderPlaylist,
    ProviderTrack,
)

SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_PLAYLIST_URL = "https://api.spotify.com/v1/playlists/{playlist_id}"
SPOTIFY_CURRENT_USER_PLAYLIST_URL = "https://api.spotify.com/v1/me/playlists"
SPOTIFY_PLAYLIST_TRACKS_URL = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"


class SpotifyAccessTokenRequiredError(Exception):
    pass


class SpotifyAdapter(MusicProviderAdapter):
    provider = "spotify"

    async def search_tracks(
        self,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        if user_token is None:
            raise SpotifyAccessTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                SPOTIFY_SEARCH_URL,
                params={
                    "q": query,
                    "type": "track",
                    "limit": 10,
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )

        if response.is_error:
            self._raise_provider_error(response)
        data = response.json()
        return [
            ProviderTrack(
                provider=self.provider,
                provider_track_id=item["id"],
                title=item["name"],
                artist_name=item["artists"][0]["name"],
                album_name=item["album"]["name"],
                duration_ms=item["duration_ms"],
                isrc=item.get("external_ids", {}).get("isrc"),
                provider_url=item.get("external_urls", {}).get("spotify"),
            )
            for item in data["tracks"]["items"]
        ]

    async def get_playlist(
        self,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        if user_token is None:
            raise SpotifyAccessTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                SPOTIFY_PLAYLIST_URL.format(playlist_id=playlist_id),
                headers={"Authorization": f"Bearer {user_token}"},
            )
        if response.is_error:
            self._raise_provider_error(response)
        data = response.json()

        tracks = [
            ProviderTrack(
                provider=self.provider,
                provider_track_id=item["track"]["id"],
                title=item["track"]["name"],
                artist_name=item["track"]["artists"][0]["name"],
                album_name=item["track"]["album"]["name"],
                duration_ms=item["track"]["duration_ms"],
                isrc=item["track"].get("external_ids", {}).get("isrc"),
                provider_url=item["track"].get("external_urls", {}).get("spotify"),
            )
            for item in data["tracks"]["items"]
            if item.get("track") is not None
        ]

        return ProviderPlaylist(
            provider=self.provider,
            provider_playlist_id=data["id"],
            title=data["name"],
            tracks=tracks,
            provider_url=data.get("external_urls", {}).get("spotify"),
        )

    async def create_playlist(
        self,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        if not user_token:
            raise SpotifyAccessTokenRequiredError()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPOTIFY_CURRENT_USER_PLAYLIST_URL,
                json={
                    "name": input_data.title,
                    "description": input_data.description or "",
                    "public": False,
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )

        if response.is_error:
            self._raise_provider_error(response)
        data = response.json()

        return ProviderPlaylist(
            provider=self.provider,
            provider_playlist_id=data["id"],
            title=data["name"],
            tracks=[],
            provider_url=data.get("external_urls", {}).get("spotify"),
        )

    async def add_tracks_to_playlist(
        self,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        if not user_token:
            raise SpotifyAccessTokenRequiredError()

        uris = [f"spotify:track:{track_id}" for track_id in track_ids]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
                json={"uris": uris},
                headers={"Authorization": f"Bearer {user_token}"},
            )
        if response.is_error:
            self._raise_provider_error(response)

    def build_open_url(self, item: Any) -> str:
        provider_id = self._extract_provider_id(item)
        return f"https://open.spotify.com/track/{provider_id}"