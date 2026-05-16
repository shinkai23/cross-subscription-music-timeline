import pytest

from app.providers.base import (
    CreatePlaylistInput,
    ProviderPlaybackMetadata,
    ProviderPlaylist,
    ProviderTrack,
)
from app.services.provider_service import ProviderService


class FakeAdapter:
    provider = "fake"

    async def search_tracks(
        self,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        assert query == "Radiohead"
        assert user_token == "user-token"
        return [
            ProviderTrack(
                provider="fake",
                provider_track_id="track-1",
                title="Everything In Its Right Place",
                artist_name="Radiohead",
            )
        ]

    async def get_playlist(
        self,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        assert playlist_id == "playlist-1"
        assert user_token == "user-token"
        return ProviderPlaylist(
            provider="fake",
            provider_playlist_id="playlist-1",
            title="Favorites",
        )

    async def create_playlist(
        self,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        assert input_data.title == "New Playlist"
        assert user_token == "user-token"
        return ProviderPlaylist(
            provider="fake",
            provider_playlist_id="playlist-1",
            title=input_data.title,
        )

    async def add_tracks_to_playlist(
        self,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        assert playlist_id == "playlist-1"
        assert track_ids == ["track-1", "track-2"]
        assert user_token == "user-token"

    async def get_track_playback(
        self,
        track_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaybackMetadata:
        assert track_id == "track-1"
        assert user_token == "user-token"
        return ProviderPlaybackMetadata(
            provider="fake",
            provider_track_id="track-1",
            playback_id="track-1",
            preview_url="https://example.com/preview.mp3",
            artwork_url="https://example.com/artwork.jpg",
            provider_url="https://example.com/track/track-1",
            is_playable=True,
        )


@pytest.mark.anyio
async def test_search_tracks_calls_provider_adapter(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    service = ProviderService()

    tracks = await service.search_tracks(
        provider="fake",
        query="Radiohead",
        user_token="user-token",
    )

    assert len(tracks) == 1
    assert tracks[0].provider == "fake"
    assert tracks[0].provider_track_id == "track-1"


@pytest.mark.anyio
async def test_get_playlist_calls_provider_adapter(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    service = ProviderService()

    playlist = await service.get_playlist(
        provider="fake",
        playlist_id="playlist-1",
        user_token="user-token",
    )

    assert playlist.provider == "fake"
    assert playlist.provider_playlist_id == "playlist-1"


@pytest.mark.anyio
async def test_create_playlist_calls_provider_adapter(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    service = ProviderService()

    playlist = await service.create_playlist(
        provider="fake",
        input_data=CreatePlaylistInput(title="New Playlist"),
        user_token="user-token",
    )

    assert playlist.provider == "fake"
    assert playlist.provider_playlist_id == "playlist-1"


@pytest.mark.anyio
async def test_add_tracks_to_playlist_calls_provider_adapter(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    service = ProviderService()

    await service.add_tracks_to_playlist(
        provider="fake",
        playlist_id="playlist-1",
        track_ids=["track-1", "track-2"],
        user_token="user-token",
    )


@pytest.mark.anyio
async def test_get_track_playback_calls_provider_adapter(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    service = ProviderService()

    playback = await service.get_track_playback(
        provider="fake",
        track_id="track-1",
        user_token="user-token",
    )

    assert playback.provider == "fake"
    assert playback.provider_track_id == "track-1"
    assert playback.preview_url == "https://example.com/preview.mp3"
