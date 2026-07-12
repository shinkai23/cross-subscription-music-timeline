import pytest

from app.providers.base import (
    CreatePlaylistInput,
    ProviderPlaybackMetadata,
    ProviderPlaylist,
    ProviderTrack,
)
from app.services.provider_service import ProviderService


class FakeTrack:
    id = "canonical-track-1"


class FakeProviderTrack:
    id = "existing-provider-track-row-1"
    track_id = "existing-canonical-track-1"


class FakeTrackRepository:
    def __init__(self) -> None:
        self.playback: ProviderPlaybackMetadata | None = None

    def get_or_create_from_playback(
        self,
        playback: ProviderPlaybackMetadata,
    ) -> FakeTrack:
        self.playback = playback
        return FakeTrack()


class FakeProviderTrackRepository:
    def __init__(self) -> None:
        self.track_id: str | None = None
        self.playback: ProviderPlaybackMetadata | None = None
        self.existing_provider_track = None

    def get_by_provider_track_id(
        self,
        provider: str,
        provider_track_id: str,
    ):
        assert provider == "fake"
        assert provider_track_id == "track-1"
        return self.existing_provider_track

    def upsert_playback_metadata(
        self,
        track_id: str,
        playback: ProviderPlaybackMetadata,
    ) -> FakeProviderTrack:
        self.track_id = track_id
        self.playback = playback
        saved_provider_track = FakeProviderTrack()
        saved_provider_track.id = "provider-track-row-1"
        return saved_provider_track


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
                artwork_url="https://example.com/search-artwork.jpg",
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
            title="Everything In Its Right Place",
            artist_name="Radiohead",
            album_name="Kid A",
            duration_ms=251000,
            metadata={"source": "fake"},
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
    assert tracks[0].artwork_url == "https://example.com/search-artwork.jpg"


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
    assert playback.track_id is None
    assert playback.provider_track_row_id is None


@pytest.mark.anyio
async def test_get_track_playback_persists_canonical_and_provider_track(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    track_repository = FakeTrackRepository()
    provider_track_repository = FakeProviderTrackRepository()
    service = ProviderService(
        track_repository=track_repository,
        provider_track_repository=provider_track_repository,
    )

    playback = await service.get_track_playback(
        provider="fake",
        track_id="track-1",
        user_token="user-token",
    )

    assert track_repository.playback is not None
    assert track_repository.playback.provider == playback.provider
    assert track_repository.playback.provider_track_id == playback.provider_track_id
    assert provider_track_repository.track_id == "canonical-track-1"
    assert provider_track_repository.playback is not None
    assert provider_track_repository.playback.provider == playback.provider
    assert provider_track_repository.playback.provider_track_id == (
        playback.provider_track_id
    )
    assert playback.track_id == "canonical-track-1"
    assert playback.provider_track_row_id == "provider-track-row-1"


@pytest.mark.anyio
async def test_get_track_playback_reuses_existing_provider_track(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeAdapter(),
    )
    track_repository = FakeTrackRepository()
    provider_track_repository = FakeProviderTrackRepository()
    provider_track_repository.existing_provider_track = FakeProviderTrack()
    service = ProviderService(
        track_repository=track_repository,
        provider_track_repository=provider_track_repository,
    )

    playback = await service.get_track_playback(
        provider="fake",
        track_id="track-1",
        user_token="user-token",
    )

    assert track_repository.playback is None
    assert provider_track_repository.track_id == "existing-canonical-track-1"
    assert provider_track_repository.playback is not None
    assert provider_track_repository.playback.provider == playback.provider
    assert provider_track_repository.playback.provider_track_id == (
        playback.provider_track_id
    )
    assert playback.track_id == "existing-canonical-track-1"
    assert playback.provider_track_row_id == "provider-track-row-1"
