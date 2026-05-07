from abc import ABC, abstractmethod
from typing import Any, Protocol

from pydantic import BaseModel, Field


class ProviderTrack(BaseModel):
    provider: str
    provider_track_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    isrc: str | None = None
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


class ProviderItemRef(Protocol):
    provider_id: str


class MusicProviderAdapter(ABC):
    provider: str

    @abstractmethod
    async def search_tracks(self, query: str, user_token: str | None = None) -> list[ProviderTrack]:
        raise NotImplementedError

    @abstractmethod
    async def get_playlist(self, playlist_id: str, user_token: str | None = None) -> ProviderPlaylist:
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
    def build_open_url(self, item: ProviderItemRef | dict[str, Any] | str) -> str:
        raise NotImplementedError
