from fastapi.testclient import TestClient

from app.main import app
from app.providers.base import CreatePlaylistInput, ProviderPlaylist, ProviderTrack
from app.routers.provider_router import get_provider_service


class FakeProviderService:
    async def search_tracks(
        self,
        provider: str,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        assert provider == "spotify"
        assert query == "Radiohead"
        assert user_token == "access-token"
        return [
            ProviderTrack(
                provider="spotify",
                provider_track_id="track-1",
                title="Everything In Its Right Place",
                artist_name="Radiohead",
                album_name="Kid A",
                duration_ms=251000,
                isrc="GBAYE0000811",
                provider_url="https://open.spotify.com/track/track-1",
            )
        ]

    async def get_playlist(
        self,
        provider: str,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        assert provider == "spotify"
        assert playlist_id == "playlist-1"
        assert user_token == "access-token"
        return ProviderPlaylist(
            provider="spotify",
            provider_playlist_id="playlist-1",
            title="Favorites",
            tracks=[
                ProviderTrack(
                    provider="spotify",
                    provider_track_id="track-1",
                    title="Everything In Its Right Place",
                    artist_name="Radiohead",
                )
            ],
            provider_url="https://open.spotify.com/playlist/playlist-1",
        )

    async def create_playlist(
        self,
        provider: str,
        input_data: CreatePlaylistInput,
        user_token: str,
    ) -> ProviderPlaylist:
        assert provider == "spotify"
        assert input_data.title == "New Playlist"
        assert input_data.description == "Created from app"
        assert user_token == "access-token"
        return ProviderPlaylist(
            provider="spotify",
            provider_playlist_id="playlist-1",
            title=input_data.title,
            tracks=[],
            provider_url="https://open.spotify.com/playlist/playlist-1",
        )

    async def add_tracks_to_playlist(
        self,
        provider: str,
        playlist_id: str,
        track_ids: list[str],
        user_token: str,
    ) -> None:
        assert provider == "spotify"
        assert playlist_id == "playlist-1"
        assert track_ids == ["track-1", "track-2"]
        assert user_token == "access-token"


def test_search_tracks(client: TestClient) -> None:
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    try:
        response = client.get(
            "/providers/spotify/search/tracks",
            params={
                "q": "Radiohead",
                "user_token": "access-token",
            },
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)

    assert response.status_code == 200
    assert response.json() == [
        {
            "provider": "spotify",
            "provider_track_id": "track-1",
            "title": "Everything In Its Right Place",
            "artist_name": "Radiohead",
            "album_name": "Kid A",
            "duration_ms": 251000,
            "isrc": "GBAYE0000811",
            "provider_url": "https://open.spotify.com/track/track-1",
        }
    ]


def test_search_tracks_requires_query(client: TestClient) -> None:
    response = client.get("/providers/spotify/search/tracks")

    assert response.status_code == 422


def test_get_playlist(client: TestClient) -> None:
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    try:
        response = client.get(
            "/providers/spotify/playlists/playlist-1",
            params={"user_token": "access-token"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "provider": "spotify",
        "provider_playlist_id": "playlist-1",
        "title": "Favorites",
        "tracks": [
            {
                "provider": "spotify",
                "provider_track_id": "track-1",
                "title": "Everything In Its Right Place",
                "artist_name": "Radiohead",
                "album_name": None,
                "duration_ms": None,
                "isrc": None,
                "provider_url": None,
            }
        ],
        "provider_url": "https://open.spotify.com/playlist/playlist-1",
    }


def test_create_playlist(client: TestClient) -> None:
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    try:
        response = client.post(
            "/providers/spotify/playlists",
            params={"user_token": "access-token"},
            json={
                "title": "New Playlist",
                "description": "Created from app",
                "track_ids": [],
            },
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "provider": "spotify",
        "provider_playlist_id": "playlist-1",
        "title": "New Playlist",
        "tracks": [],
        "provider_url": "https://open.spotify.com/playlist/playlist-1",
    }


def test_create_playlist_requires_user_token(client: TestClient) -> None:
    response = client.post(
        "/providers/spotify/playlists",
        json={
            "title": "New Playlist",
            "description": "Created from app",
            "track_ids": [],
        },
    )

    assert response.status_code == 422


def test_add_tracks_to_playlist(client: TestClient) -> None:
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    try:
        response = client.post(
            "/providers/spotify/playlists/playlist-1/tracks",
            params={"user_token": "access-token"},
            json={"track_ids": ["track-1", "track-2"]},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_tracks_to_playlist_requires_user_token(client: TestClient) -> None:
    response = client.post(
        "/providers/spotify/playlists/playlist-1/tracks",
        json={"track_ids": ["track-1"]},
    )

    assert response.status_code == 422


def test_add_tracks_to_playlist_rejects_empty_track_ids(client: TestClient) -> None:
    response = client.post(
        "/providers/spotify/playlists/playlist-1/tracks",
        params={"user_token": "access-token"},
        json={"track_ids": []},
    )

    assert response.status_code == 422
