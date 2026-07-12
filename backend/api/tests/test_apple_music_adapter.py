from dataclasses import dataclass

import httpx
import pytest

from app.providers.apple_music_adapter import AppleMusicAdapter
from app.providers.apple_music_adapter import (
    APPLE_MUSIC_CATALOG_SONG_URL,
    APPLE_MUSIC_LIBRARY_PLAYLIST_URL,
    APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL,
    APPLE_MUSIC_LIBRARY_PLAYLISTS_URL,
    APPLE_MUSIC_SEARCH_URL,
    AppleMusicDeveloperTokenRequiredError,
    AppleMusicUserTokenRequiredError,
)
from app.providers.base import CreatePlaylistInput, ProviderTrack
from app.providers.error import ProviderApiError


@dataclass
class AppleMusicTestSettings:
    apple_music_developer_token: str = "developer-token"
    apple_music_storefront: str = "us"


@pytest.mark.anyio
async def test_search_tracks_requires_developer_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(apple_music_developer_token=""),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicDeveloperTokenRequiredError):
        await adapter.search_tracks(query="Radiohead")


@pytest.mark.anyio
async def test_search_tracks_maps_apple_music_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).startswith(
            APPLE_MUSIC_SEARCH_URL.format(storefront="us")
        )
        assert request.url.params["term"] == "Radiohead"
        assert request.url.params["types"] == "songs"
        assert request.url.params["limit"] == "10"
        assert request.headers["Authorization"] == "Bearer developer-token"
        return httpx.Response(
            status_code=200,
            json={
                "results": {
                    "songs": {
                        "data": [
                            {
                                "id": "apple-track-1",
                                "attributes": {
                                    "name": "Everything In Its Right Place",
                                    "artistName": "Radiohead",
                                    "albumName": "Kid A",
                                    "durationInMillis": 251000,
                                    "isrc": "GBAYE0000811",
                                    "artwork": {
                                        "url": "https://is1-ssl.mzstatic.com/image/{w}x{h}bb.jpg",
                                        "width": 600,
                                        "height": 600,
                                    },
                                    "url": "https://music.apple.com/song/1",
                                },
                            }
                        ]
                    }
                }
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.apple_music_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = AppleMusicAdapter()

    tracks = await adapter.search_tracks(query="Radiohead")

    assert len(tracks) == 1
    assert tracks[0].provider == "apple_music"
    assert tracks[0].provider_track_id == "apple-track-1"
    assert tracks[0].title == "Everything In Its Right Place"
    assert tracks[0].artist_name == "Radiohead"
    assert tracks[0].album_name == "Kid A"
    assert tracks[0].duration_ms == 251000
    assert tracks[0].isrc == "GBAYE0000811"
    assert (
        tracks[0].artwork_url
        == "https://is1-ssl.mzstatic.com/image/600x600bb.jpg"
    )
    assert tracks[0].provider_url == "https://music.apple.com/song/1"


@pytest.mark.anyio
async def test_search_tracks_raises_provider_api_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=500, json={"errors": []})

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.apple_music_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(ProviderApiError) as exc_info:
        await adapter.search_tracks(query="Radiohead")

    assert exc_info.value.provider == "apple_music"
    assert exc_info.value.status_code == 500
    assert exc_info.value.message == "Provider API request failed"


@pytest.mark.anyio
async def test_get_playlist_requires_developer_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(apple_music_developer_token=""),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicDeveloperTokenRequiredError):
        await adapter.get_playlist(
            playlist_id="library-playlist-1",
            user_token="music-user-token",
        )


@pytest.mark.anyio
async def test_get_playlist_requires_user_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicUserTokenRequiredError):
        await adapter.get_playlist(playlist_id="library-playlist-1")


@pytest.mark.anyio
async def test_get_playlist_maps_apple_music_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == APPLE_MUSIC_LIBRARY_PLAYLIST_URL.format(
            playlist_id="library-playlist-1"
        )
        assert request.headers["Authorization"] == "Bearer developer-token"
        assert request.headers["Music-User-Token"] == "music-user-token"
        return httpx.Response(
            status_code=200,
            json={
                "data": [
                    {
                        "id": "library-playlist-1",
                        "attributes": {
                            "name": "Library Favorites",
                            "url": "https://music.apple.com/playlist/1",
                        },
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.apple_music_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = AppleMusicAdapter()

    playlist = await adapter.get_playlist(
        playlist_id="library-playlist-1",
        user_token="music-user-token",
    )

    assert playlist.provider == "apple_music"
    assert playlist.provider_playlist_id == "library-playlist-1"
    assert playlist.title == "Library Favorites"
    assert playlist.tracks == []
    assert playlist.provider_url == "https://music.apple.com/playlist/1"


@pytest.mark.anyio
async def test_create_playlist_requires_developer_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(apple_music_developer_token=""),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicDeveloperTokenRequiredError):
        await adapter.create_playlist(
            input_data=CreatePlaylistInput(title="New Playlist"),
            user_token="music-user-token",
        )


@pytest.mark.anyio
async def test_create_playlist_requires_user_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicUserTokenRequiredError):
        await adapter.create_playlist(
            input_data=CreatePlaylistInput(title="New Playlist"),
            user_token="",
        )


@pytest.mark.anyio
async def test_create_playlist_maps_apple_music_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == APPLE_MUSIC_LIBRARY_PLAYLISTS_URL
        assert request.headers["Authorization"] == "Bearer developer-token"
        assert request.headers["Music-User-Token"] == "music-user-token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.method == "POST"
        assert request.content == (
            b'{"attributes":{"name":"New Playlist",'
            b'"description":"Created from app"}}'
        )
        return httpx.Response(
            status_code=201,
            json={
                "data": [
                    {
                        "id": "library-playlist-1",
                        "attributes": {
                            "name": "New Playlist",
                            "url": "https://music.apple.com/playlist/1",
                        },
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.apple_music_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = AppleMusicAdapter()

    playlist = await adapter.create_playlist(
        input_data=CreatePlaylistInput(
            title="New Playlist",
            description="Created from app",
        ),
        user_token="music-user-token",
    )

    assert playlist.provider == "apple_music"
    assert playlist.provider_playlist_id == "library-playlist-1"
    assert playlist.title == "New Playlist"
    assert playlist.tracks == []
    assert playlist.provider_url == "https://music.apple.com/playlist/1"


@pytest.mark.anyio
async def test_add_tracks_to_playlist_requires_developer_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(apple_music_developer_token=""),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicDeveloperTokenRequiredError):
        await adapter.add_tracks_to_playlist(
            playlist_id="library-playlist-1",
            track_ids=["apple-track-1"],
            user_token="music-user-token",
        )


@pytest.mark.anyio
async def test_add_tracks_to_playlist_requires_user_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicUserTokenRequiredError):
        await adapter.add_tracks_to_playlist(
            playlist_id="library-playlist-1",
            track_ids=["apple-track-1"],
            user_token="",
        )


@pytest.mark.anyio
async def test_add_tracks_to_playlist_posts_track_relationships(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL.format(
            playlist_id="library-playlist-1"
        )
        assert request.headers["Authorization"] == "Bearer developer-token"
        assert request.headers["Music-User-Token"] == "music-user-token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.method == "POST"
        assert request.content == (
            b'{"data":[{"id":"apple-track-1","type":"songs"},'
            b'{"id":"apple-track-2","type":"songs"}]}'
        )
        return httpx.Response(status_code=202)

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.apple_music_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = AppleMusicAdapter()

    await adapter.add_tracks_to_playlist(
        playlist_id="library-playlist-1",
        track_ids=["apple-track-1", "apple-track-2"],
        user_token="music-user-token",
    )


@pytest.mark.anyio
async def test_get_track_playback_requires_developer_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(apple_music_developer_token=""),
    )
    adapter = AppleMusicAdapter()

    with pytest.raises(AppleMusicDeveloperTokenRequiredError):
        await adapter.get_track_playback(track_id="apple-track-1")


@pytest.mark.anyio
async def test_get_track_playback_maps_apple_music_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == APPLE_MUSIC_CATALOG_SONG_URL.format(
            storefront="us",
            track_id="apple-track-1",
        )
        assert request.headers["Authorization"] == "Bearer developer-token"
        assert request.headers["Music-User-Token"] == "music-user-token"
        return httpx.Response(
            status_code=200,
            json={
                "data": [
                    {
                            "id": "apple-track-1",
                            "attributes": {
                                "name": "Apple Track",
                                "artistName": "Apple Artist",
                                "albumName": "Apple Album",
                                "durationInMillis": 210000,
                                "isrc": "GBAYE0000811",
                                "genreNames": ["Alternative"],
                                "url": "https://music.apple.com/song/apple-track-1",
                                "previews": [
                                    {"url": "https://audio-ssl.itunes.apple.com/preview"}
                                ],
                            "artwork": {
                                "url": "https://is1-ssl.mzstatic.com/image/{w}x{h}bb.jpg",
                                "width": 600,
                                "height": 600,
                            },
                            "playParams": {
                                "id": "apple-track-1",
                                "kind": "song",
                            },
                        },
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.apple_music_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = AppleMusicAdapter()

    playback = await adapter.get_track_playback(
        track_id="apple-track-1",
        user_token="music-user-token",
    )

    assert playback.provider == "apple_music"
    assert playback.provider_track_id == "apple-track-1"
    assert playback.title == "Apple Track"
    assert playback.artist_name == "Apple Artist"
    assert playback.album_name == "Apple Album"
    assert playback.duration_ms == 210000
    assert playback.isrc == "GBAYE0000811"
    assert playback.metadata == {
        "genre_names": ["Alternative"],
        "play_params": {"id": "apple-track-1", "kind": "song"},
    }
    assert playback.playback_id == "apple-track-1"
    assert playback.preview_url == "https://audio-ssl.itunes.apple.com/preview"
    assert (
        playback.artwork_url
        == "https://is1-ssl.mzstatic.com/image/600x600bb.jpg"
    )
    assert playback.provider_url == "https://music.apple.com/song/apple-track-1"
    assert playback.is_playable is True


def test_build_open_url_from_string() -> None:
    adapter = AppleMusicAdapter()

    url = adapter.build_open_url("apple-track-1")

    assert url == "https://music.apple.com/song/apple-track-1"


def test_build_open_url_from_dict() -> None:
    adapter = AppleMusicAdapter()

    url = adapter.build_open_url({"provider_track_id": "apple-track-1"})

    assert url == "https://music.apple.com/song/apple-track-1"


def test_build_open_url_from_provider_track() -> None:
    adapter = AppleMusicAdapter()
    track = ProviderTrack(
        provider="apple_music",
        provider_track_id="apple-track-1",
        title="Song",
        artist_name="Artist",
    )

    url = adapter.build_open_url(track)

    assert url == "https://music.apple.com/song/apple-track-1"
