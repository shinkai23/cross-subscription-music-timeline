from abc import ABC, abstractmethod
from typing import Any, Protocol

import httpx

from pydantic import BaseModel, Field

from app.providers.error import ProviderApiError


class ProviderTrack(BaseModel):
    provider: str
    provider_track_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    isrc: str | None = None
    artwork_url: str | None = None
    provider_url: str | None = None


class ProviderPlaylist(BaseModel):
    provider: str
    provider_playlist_id: str
    title: str
    tracks: list[ProviderTrack] = Field(default_factory=list)
    provider_url: str | None = None


class CreatePlaylistInput(BaseModel):
    title: str
    description: str | None = None
    track_ids: list[str] = Field(default_factory=list)


class ProviderPlaybackMetadata(BaseModel):
    provider: str
    provider_track_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    isrc: str | None = None
    metadata: dict | None = None
    playback_id: str
    preview_url: str | None = None
    artwork_url: str | None = None
    provider_url: str | None = None
    is_playable: bool = True


class ProviderItemRef(Protocol):
    provider_id: str


class MusicProviderAdapter(ABC):
    provider: str

    @abstractmethod
    async def search_tracks(
        self,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        raise NotImplementedError

    @abstractmethod
    async def get_playlist(
        self,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        raise NotImplementedError

    @abstractmethod
    async def create_playlist(
        self,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        raise NotImplementedError

    @abstractmethod
    async def add_tracks_to_playlist(
        self,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_track_playback(
        self,
        track_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaybackMetadata:
        raise NotImplementedError

    @abstractmethod
    def build_open_url(self, item: ProviderItemRef | dict[str, Any] | str) -> str:
        raise NotImplementedError

    def _raise_provider_error(self, response: httpx.Response) -> None:
        raise ProviderApiError(
            provider=self.provider,
            status_code=response.status_code,
            message=self._build_provider_error_message(response.status_code),
        )

    def _build_provider_error_message(self, status_code: int) -> str:
        if status_code == 401:
            return "Provider access token is invalid"
        if status_code == 403:
            return "Provider permission denied"
        if status_code == 404:
            return "Provider resource not found"
        if status_code == 429:
            return "Provider rate limit exceeded"
        return "Provider API request failed"

    def _extract_provider_id(self, item: ProviderItemRef | dict[str, Any] | str) -> str:
        if isinstance(item, str):
            return item

        if isinstance(item, dict):
            provider_id = (
                item.get("provider_track_id")
                or item.get("provider_id")
                or item.get("id")
            )
        else:
            provider_id = (
                getattr(item, "provider_track_id", None)
                or getattr(item, "provider_id", None)
                or getattr(item, "id", None)
            )

        if provider_id is None:
            raise ValueError("Provider item id is required")

        return provider_id
