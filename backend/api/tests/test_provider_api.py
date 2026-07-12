import httpx
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.main import app
from app.models.service_account import ServiceAccount
from app.models.user import User
from app.providers.apple_music_adapter import (
    APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL,
    APPLE_MUSIC_LIBRARY_PLAYLIST_URL,
    APPLE_MUSIC_LIBRARY_PLAYLISTS_URL,
)
from app.providers.base import (
    CreatePlaylistInput,
    ProviderPlaybackMetadata,
    ProviderPlaylist,
    ProviderTrack,
)
from app.providers.error import ProviderApiError
from app.routers.provider_router import (
    get_provider_service,
    get_service_account_service,
)
from app.services.service_account_errors import ServiceAccountNotConnectedError
from app.services.token_encryption_service import TokenEncryptionService


class AppleMusicTestSettings:
    apple_music_developer_token = "developer-token"
    apple_music_storefront = "us"


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
                artwork_url="https://example.com/artwork.jpg",
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

    async def get_track_playback(
        self,
        provider: str,
        track_id: str,
        user_token: str,
    ) -> ProviderPlaybackMetadata:
        assert provider == "spotify"
        assert track_id == "track-1"
        assert user_token == "access-token"
        return ProviderPlaybackMetadata(
            provider="spotify",
            provider_track_id="track-1",
            title="Test Track",
            artist_name="Test Artist",
            album_name="Test Album",
            duration_ms=180000,
            metadata={"source": "fake"},
            playback_id="track-1",
            preview_url="https://p.scdn.co/mp3-preview/track",
            artwork_url="https://i.scdn.co/image/artwork",
            provider_url="https://open.spotify.com/track/track-1",
            is_playable=True,
        )


class FakeAppleMusicProviderService:
    async def get_playlist(
        self,
        provider: str,
        playlist_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaylist:
        assert provider == "apple_music"
        assert playlist_id == "library-playlist-1"
        assert user_token == "music-user-token"
        return ProviderPlaylist(
            provider="apple_music",
            provider_playlist_id="library-playlist-1",
            title="Library Favorites",
            tracks=[],
            provider_url="https://music.apple.com/playlist/1",
        )


class FakeServiceAccountService:
    async def get_provider_access_token(
        self,
        user: User,
        provider: str,
    ) -> str:
        assert user.handle == "test-user"
        assert provider == "spotify"
        return "access-token"


class FakeProviderRateLimitService:
    async def search_tracks(
        self,
        provider: str,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        raise ProviderApiError(
            provider=provider,
            status_code=429,
            message="Provider rate limit exceeded",
        )


class FakeProviderServerErrorService:
    async def search_tracks(
        self,
        provider: str,
        query: str,
        user_token: str | None = None,
    ) -> list[ProviderTrack]:
        raise ProviderApiError(
            provider=provider,
            status_code=500,
            message="Provider API request failed",
        )


class FakeDisconnectedServiceAccountService:
    async def get_provider_access_token(
        self,
        user: User,
        provider: str,
    ) -> str:
        assert user.handle == "test-user"
        assert provider == "spotify"
        raise ServiceAccountNotConnectedError()


def test_search_tracks(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.get(
            "/providers/spotify/search/tracks",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": "Radiohead"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

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
            "artwork_url": "https://example.com/artwork.jpg",
            "provider_url": "https://open.spotify.com/track/track-1",
        }
    ]


def test_search_tracks_requires_query(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )

    try:
        response = client.get(
            "/providers/spotify/search/tracks",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 422


def test_search_tracks_requires_authentication(client: TestClient) -> None:
    response = client.get(
        "/providers/spotify/search/tracks",
        params={"q": "Radiohead"},
    )

    assert response.status_code == 401


def test_search_tracks_requires_connected_provider(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeDisconnectedServiceAccountService()
    )
    try:
        response = client.get(
            "/providers/spotify/search/tracks",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": "Radiohead"},
        )
    finally:
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 409
    assert response.json() == {"detail": "Provider account is not connected"}


def test_search_tracks_returns_provider_rate_limit_error(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = (
        lambda: FakeProviderRateLimitService()
    )
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.get(
            "/providers/spotify/search/tracks",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": "Radiohead"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 429
    assert response.json() == {
        "detail": {
            "provider": "spotify",
            "message": "Provider rate limit exceeded",
        }
    }


def test_search_tracks_returns_bad_gateway_for_provider_server_error(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = (
        lambda: FakeProviderServerErrorService()
    )
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.get(
            "/providers/spotify/search/tracks",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": "Radiohead"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 502
    assert response.json() == {
        "detail": {
            "provider": "spotify",
            "message": "Provider API request failed",
        }
    }


def test_get_playlist(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.get(
            "/providers/spotify/playlists/playlist-1",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

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
                "artwork_url": None,
                "provider_url": None,
            }
        ],
        "provider_url": "https://open.spotify.com/playlist/playlist-1",
    }


def test_get_playlist_requires_authentication(client: TestClient) -> None:
    response = client.get("/providers/spotify/playlists/playlist-1")

    assert response.status_code == 401


def test_get_apple_music_playlist_uses_connected_music_user_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.add(
        ServiceAccount(
            user_id=user.id,
            provider="apple_music",
            provider_user_id="apple-user-1",
            encrypted_refresh_token=TokenEncryptionService().encrypt(
                "music-user-token"
            ),
        )
    )
    db_session.commit()
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = (
        lambda: FakeAppleMusicProviderService()
    )

    try:
        response = client.get(
            "/providers/apple_music/playlists/library-playlist-1",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "provider": "apple_music",
        "provider_playlist_id": "library-playlist-1",
        "title": "Library Favorites",
        "tracks": [],
        "provider_url": "https://music.apple.com/playlist/1",
    }


def test_get_apple_music_playlist_calls_adapter_with_connected_music_user_token(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.add(
        ServiceAccount(
            user_id=user.id,
            provider="apple_music",
            provider_user_id="apple-user-1",
            encrypted_refresh_token=TokenEncryptionService().encrypt(
                "music-user-token"
            ),
        )
    )
    db_session.commit()
    token = create_access_token(subject=user.id)
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

    response = client.get(
        "/providers/apple_music/playlists/library-playlist-1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "apple_music",
        "provider_playlist_id": "library-playlist-1",
        "title": "Library Favorites",
        "tracks": [],
        "provider_url": "https://music.apple.com/playlist/1",
    }


def test_create_playlist(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.post(
            "/providers/spotify/playlists",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "New Playlist",
                "description": "Created from app",
                "track_ids": [],
            },
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "provider": "spotify",
        "provider_playlist_id": "playlist-1",
        "title": "New Playlist",
        "tracks": [],
        "provider_url": "https://open.spotify.com/playlist/playlist-1",
    }


def test_create_apple_music_playlist_calls_adapter_with_connected_music_user_token(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.add(
        ServiceAccount(
            user_id=user.id,
            provider="apple_music",
            provider_user_id="apple-user-1",
            encrypted_refresh_token=TokenEncryptionService().encrypt(
                "music-user-token"
            ),
        )
    )
    db_session.commit()
    token = create_access_token(subject=user.id)
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == APPLE_MUSIC_LIBRARY_PLAYLISTS_URL
        assert request.method == "POST"
        assert request.headers["Authorization"] == "Bearer developer-token"
        assert request.headers["Music-User-Token"] == "music-user-token"
        assert request.headers["Content-Type"] == "application/json"
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

    response = client.post(
        "/providers/apple_music/playlists",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "New Playlist",
            "description": "Created from app",
            "track_ids": [],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "apple_music",
        "provider_playlist_id": "library-playlist-1",
        "title": "New Playlist",
        "tracks": [],
        "provider_url": "https://music.apple.com/playlist/1",
    }


def test_create_playlist_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/providers/spotify/playlists",
        json={
            "title": "New Playlist",
            "description": "Created from app",
            "track_ids": [],
        },
    )

    assert response.status_code == 401


def test_add_tracks_to_playlist(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.post(
            "/providers/spotify/playlists/playlist-1/tracks",
            headers={"Authorization": f"Bearer {token}"},
            json={"track_ids": ["track-1", "track-2"]},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_tracks_to_apple_music_playlist_calls_adapter_with_connected_token(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    db_session.add(
        ServiceAccount(
            user_id=user.id,
            provider="apple_music",
            provider_user_id="apple-user-1",
            encrypted_refresh_token=TokenEncryptionService().encrypt(
                "music-user-token"
            ),
        )
    )
    db_session.commit()
    token = create_access_token(subject=user.id)
    monkeypatch.setattr(
        "app.providers.apple_music_adapter.get_settings",
        lambda: AppleMusicTestSettings(),
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == APPLE_MUSIC_LIBRARY_PLAYLIST_TRACKS_URL.format(
            playlist_id="library-playlist-1"
        )
        assert request.method == "POST"
        assert request.headers["Authorization"] == "Bearer developer-token"
        assert request.headers["Music-User-Token"] == "music-user-token"
        assert request.headers["Content-Type"] == "application/json"
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

    response = client.post(
        "/providers/apple_music/playlists/library-playlist-1/tracks",
        headers={"Authorization": f"Bearer {token}"},
        json={"track_ids": ["apple-track-1", "apple-track-2"]},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_tracks_to_playlist_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/providers/spotify/playlists/playlist-1/tracks",
        json={"track_ids": ["track-1"]},
    )

    assert response.status_code == 401


def test_add_tracks_to_playlist_rejects_empty_track_ids(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )

    try:
        response = client.post(
            "/providers/spotify/playlists/playlist-1/tracks",
            headers={"Authorization": f"Bearer {token}"},
            json={"track_ids": []},
        )
    finally:
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 422


def test_get_track_playback(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_provider_service] = lambda: FakeProviderService()
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )
    try:
        response = client.get(
            "/providers/spotify/tracks/track-1/playback",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_provider_service, None)
        app.dependency_overrides.pop(get_service_account_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "provider": "spotify",
        "provider_track_id": "track-1",
        "title": "Test Track",
        "artist_name": "Test Artist",
        "album_name": "Test Album",
        "duration_ms": 180000,
        "isrc": None,
        "metadata": {"source": "fake"},
        "playback_id": "track-1",
        "preview_url": "https://p.scdn.co/mp3-preview/track",
        "artwork_url": "https://i.scdn.co/image/artwork",
        "provider_url": "https://open.spotify.com/track/track-1",
        "is_playable": True,
        "track_id": None,
        "provider_track_row_id": None,
    }
