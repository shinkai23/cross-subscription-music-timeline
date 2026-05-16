import httpx
import pytest

from app.providers.base import CreatePlaylistInput, ProviderTrack
from app.providers.error import ProviderApiError
from app.providers.spotify_adapter import (
    SPOTIFY_CURRENT_USER_PLAYLIST_URL,
    SPOTIFY_PLAYLIST_TRACKS_URL,
    SPOTIFY_PLAYLIST_URL,
    SPOTIFY_SEARCH_URL,
    SPOTIFY_TRACK_URL,
    SpotifyAccessTokenRequiredError,
    SpotifyAdapter,
)


@pytest.mark.anyio
async def test_search_tracks_requires_access_token() -> None:
    adapter = SpotifyAdapter()

    with pytest.raises(SpotifyAccessTokenRequiredError):
        await adapter.search_tracks(query="Daft Punk")


@pytest.mark.anyio
async def test_search_tracks_maps_spotify_response(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).startswith(SPOTIFY_SEARCH_URL)
        assert request.url.params["q"] == "Daft Punk"
        assert request.url.params["type"] == "track"
        assert request.url.params["limit"] == "10"
        assert request.headers["Authorization"] == "Bearer access-token"
        return httpx.Response(
            status_code=200,
            json={
                "tracks": {
                    "items": [
                        {
                            "id": "spotify-track-1",
                            "name": "One More Time",
                            "artists": [{"name": "Daft Punk"}],
                            "album": {"name": "Discovery"},
                            "duration_ms": 320000,
                            "external_ids": {"isrc": "GBDUW0000053"},
                            "external_urls": {
                                "spotify": "https://open.spotify.com/track/1"
                            },
                        }
                    ]
                }
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.spotify_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = SpotifyAdapter()

    tracks = await adapter.search_tracks(
        query="Daft Punk",
        user_token="access-token",
    )

    assert len(tracks) == 1
    assert tracks[0].provider == "spotify"
    assert tracks[0].provider_track_id == "spotify-track-1"
    assert tracks[0].title == "One More Time"
    assert tracks[0].artist_name == "Daft Punk"
    assert tracks[0].album_name == "Discovery"
    assert tracks[0].duration_ms == 320000
    assert tracks[0].isrc == "GBDUW0000053"
    assert tracks[0].provider_url == "https://open.spotify.com/track/1"


@pytest.mark.anyio
async def test_search_tracks_raises_provider_api_error(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=429, json={"error": {"status": 429}})

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.spotify_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = SpotifyAdapter()

    with pytest.raises(ProviderApiError) as exc_info:
        await adapter.search_tracks(query="Daft Punk", user_token="access-token")

    assert exc_info.value.provider == "spotify"
    assert exc_info.value.status_code == 429
    assert exc_info.value.message == "Provider rate limit exceeded"


@pytest.mark.anyio
async def test_get_playlist_requires_access_token() -> None:
    adapter = SpotifyAdapter()

    with pytest.raises(SpotifyAccessTokenRequiredError):
        await adapter.get_playlist(playlist_id="playlist-1")


@pytest.mark.anyio
async def test_get_playlist_maps_spotify_response(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == SPOTIFY_PLAYLIST_URL.format(
            playlist_id="playlist-1"
        )
        assert request.headers["Authorization"] == "Bearer access-token"
        return httpx.Response(
            status_code=200,
            json={
                "id": "playlist-1",
                "name": "Favorites",
                "external_urls": {
                    "spotify": "https://open.spotify.com/playlist/playlist-1"
                },
                "tracks": {
                    "items": [
                        {
                            "track": {
                                "id": "spotify-track-1",
                                "name": "One More Time",
                                "artists": [{"name": "Daft Punk"}],
                                "album": {"name": "Discovery"},
                                "duration_ms": 320000,
                                "external_ids": {"isrc": "GBDUW0000053"},
                                "external_urls": {
                                    "spotify": "https://open.spotify.com/track/1"
                                },
                            }
                        },
                        {"track": None},
                    ]
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.spotify_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = SpotifyAdapter()

    playlist = await adapter.get_playlist(
        playlist_id="playlist-1",
        user_token="access-token",
    )

    assert playlist.provider == "spotify"
    assert playlist.provider_playlist_id == "playlist-1"
    assert playlist.title == "Favorites"
    assert playlist.provider_url == "https://open.spotify.com/playlist/playlist-1"
    assert len(playlist.tracks) == 1
    assert playlist.tracks[0].provider_track_id == "spotify-track-1"
    assert playlist.tracks[0].title == "One More Time"
    assert playlist.tracks[0].artist_name == "Daft Punk"
    assert playlist.tracks[0].album_name == "Discovery"
    assert playlist.tracks[0].duration_ms == 320000
    assert playlist.tracks[0].isrc == "GBDUW0000053"
    assert playlist.tracks[0].provider_url == "https://open.spotify.com/track/1"


@pytest.mark.anyio
async def test_create_playlist_requires_access_token() -> None:
    adapter = SpotifyAdapter()

    with pytest.raises(SpotifyAccessTokenRequiredError):
        await adapter.create_playlist(
            input_data=CreatePlaylistInput(title="New Playlist"),
            user_token="",
        )


@pytest.mark.anyio
async def test_create_playlist_maps_spotify_response(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == SPOTIFY_CURRENT_USER_PLAYLIST_URL
        assert request.headers["Authorization"] == "Bearer access-token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.method == "POST"
        assert request.content == (
            b'{"name":"New Playlist","description":"Created from app","public":false}'
        )
        return httpx.Response(
            status_code=201,
            json={
                "id": "playlist-1",
                "name": "New Playlist",
                "external_urls": {
                    "spotify": "https://open.spotify.com/playlist/playlist-1"
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.spotify_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = SpotifyAdapter()

    playlist = await adapter.create_playlist(
        input_data=CreatePlaylistInput(
            title="New Playlist",
            description="Created from app",
        ),
        user_token="access-token",
    )

    assert playlist.provider == "spotify"
    assert playlist.provider_playlist_id == "playlist-1"
    assert playlist.title == "New Playlist"
    assert playlist.tracks == []
    assert playlist.provider_url == "https://open.spotify.com/playlist/playlist-1"


@pytest.mark.anyio
async def test_add_tracks_to_playlist_requires_access_token() -> None:
    adapter = SpotifyAdapter()

    with pytest.raises(SpotifyAccessTokenRequiredError):
        await adapter.add_tracks_to_playlist(
            playlist_id="playlist-1",
            track_ids=["spotify-track-1"],
            user_token="",
        )


@pytest.mark.anyio
async def test_add_tracks_to_playlist_posts_track_uris(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == SPOTIFY_PLAYLIST_TRACKS_URL.format(
            playlist_id="playlist-1"
        )
        assert request.headers["Authorization"] == "Bearer access-token"
        assert request.headers["Content-Type"] == "application/json"
        assert request.method == "POST"
        assert request.content == (
            b'{"uris":["spotify:track:spotify-track-1",'
            b'"spotify:track:spotify-track-2"]}'
        )
        return httpx.Response(status_code=201, json={"snapshot_id": "snapshot-1"})

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.spotify_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = SpotifyAdapter()

    await adapter.add_tracks_to_playlist(
        playlist_id="playlist-1",
        track_ids=["spotify-track-1", "spotify-track-2"],
        user_token="access-token",
    )


@pytest.mark.anyio
async def test_get_track_playback_requires_access_token() -> None:
    adapter = SpotifyAdapter()

    with pytest.raises(SpotifyAccessTokenRequiredError):
        await adapter.get_track_playback(track_id="spotify-track-1")


@pytest.mark.anyio
async def test_get_track_playback_maps_spotify_response(monkeypatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == SPOTIFY_TRACK_URL.format(
            track_id="spotify-track-1"
        )
        assert request.headers["Authorization"] == "Bearer access-token"
        return httpx.Response(
            status_code=200,
                json={
                    "id": "spotify-track-1",
                    "name": "Spotify Track",
                    "artists": [{"name": "Spotify Artist"}],
                    "duration_ms": 180000,
                    "explicit": False,
                    "popularity": 70,
                    "preview_url": "https://p.scdn.co/mp3-preview/track",
                    "is_playable": True,
                    "external_urls": {
                        "spotify": "https://open.spotify.com/track/spotify-track-1"
                    },
                    "album": {
                        "name": "Spotify Album",
                        "images": [
                            {"url": "https://i.scdn.co/image/artwork", "width": 640}
                        ]
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async_client_class = httpx.AsyncClient

    def build_client() -> httpx.AsyncClient:
        return async_client_class(transport=transport)

    monkeypatch.setattr(
        "app.providers.spotify_adapter.httpx.AsyncClient",
        build_client,
    )
    adapter = SpotifyAdapter()

    playback = await adapter.get_track_playback(
        track_id="spotify-track-1",
        user_token="access-token",
    )

    assert playback.provider == "spotify"
    assert playback.provider_track_id == "spotify-track-1"
    assert playback.title == "Spotify Track"
    assert playback.artist_name == "Spotify Artist"
    assert playback.album_name == "Spotify Album"
    assert playback.duration_ms == 180000
    assert playback.metadata == {"explicit": False, "popularity": 70}
    assert playback.playback_id == "spotify-track-1"
    assert playback.preview_url == "https://p.scdn.co/mp3-preview/track"
    assert playback.artwork_url == "https://i.scdn.co/image/artwork"
    assert playback.provider_url == "https://open.spotify.com/track/spotify-track-1"
    assert playback.is_playable is True


def test_build_open_url_from_string() -> None:
    adapter = SpotifyAdapter()

    url = adapter.build_open_url("spotify-track-1")

    assert url == "https://open.spotify.com/track/spotify-track-1"


def test_build_open_url_from_dict() -> None:
    adapter = SpotifyAdapter()

    url = adapter.build_open_url({"provider_track_id": "spotify-track-1"})

    assert url == "https://open.spotify.com/track/spotify-track-1"


def test_build_open_url_from_provider_track() -> None:
    adapter = SpotifyAdapter()
    track = ProviderTrack(
        provider="spotify",
        provider_track_id="spotify-track-1",
        title="One More Time",
        artist_name="Daft Punk",
    )

    url = adapter.build_open_url(track)

    assert url == "https://open.spotify.com/track/spotify-track-1"
