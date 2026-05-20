from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.main import app
from app.models.post import Post
from app.models.provider_track import ProviderTrack
from app.models.track import Track
from app.models.user import User
from app.providers.base import ProviderPlaybackMetadata
from app.routers.provider_router import get_service_account_service


class FakeSpotifyAdapter:
    async def get_track_playback(
        self,
        track_id: str,
        user_token: str | None = None,
    ) -> ProviderPlaybackMetadata:
        assert track_id == "spotify-track-1"
        assert user_token == "access-token"
        return ProviderPlaybackMetadata(
            provider="spotify",
            provider_track_id="spotify-track-1",
            title="Test Track",
            artist_name="Test Artist",
            album_name="Test Album",
            duration_ms=180000,
            isrc="USABC1234567",
            metadata={"source": "fake"},
            playback_id="spotify-track-1",
            preview_url="https://example.com/preview.mp3",
            artwork_url="https://example.com/artwork.jpg",
            provider_url="https://open.spotify.com/track/spotify-track-1",
            is_playable=True,
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


def test_provider_playback_then_create_post_flow(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.provider_service.get_provider_adapter",
        lambda provider: FakeSpotifyAdapter(),
    )
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    app.dependency_overrides[get_service_account_service] = (
        lambda: FakeServiceAccountService()
    )

    try:
        playback_response = client.get(
            "/providers/spotify/tracks/spotify-track-1/playback",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_service_account_service, None)

    assert playback_response.status_code == 200
    playback = playback_response.json()
    assert playback["track_id"] is not None
    assert playback["provider_track_row_id"] is not None
    assert playback["provider"] == "spotify"
    assert playback["provider_track_id"] == "spotify-track-1"
    assert playback["preview_url"] == "https://example.com/preview.mp3"

    track = db_session.scalar(select(Track).where(Track.id == playback["track_id"]))
    provider_track = db_session.scalar(
        select(ProviderTrack).where(
            ProviderTrack.id == playback["provider_track_row_id"]
        )
    )
    assert track is not None
    assert track.isrc == "USABC1234567"
    assert provider_track is not None
    assert provider_track.track_id == track.id
    assert provider_track.provider == "spotify"
    assert provider_track.provider_track_id == "spotify-track-1"

    create_post_response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider": "spotify",
            "provider_track_id": "spotify-track-1",
            "caption": "first integrated post",
        },
    )

    assert create_post_response.status_code == 201
    created_post = create_post_response.json()
    assert created_post["track_id"] == track.id
    assert created_post["source_provider_track_id"] == provider_track.id
    assert created_post["caption"] == "first integrated post"
    assert created_post["playback"]["preview_url"] == "https://example.com/preview.mp3"

    post = db_session.scalar(select(Post).where(Post.id == created_post["id"]))
    assert post is not None
    assert post.track_id == track.id
    assert post.source_provider_track_id == provider_track.id

    timeline_response = client.get("/posts")

    assert timeline_response.status_code == 200
    timeline = timeline_response.json()
    assert len(timeline["items"]) == 1
    timeline_post = timeline["items"][0]
    assert timeline_post["id"] == created_post["id"]
    assert timeline_post["track_id"] == track.id
    assert timeline_post["source_provider_track_id"] == provider_track.id
    assert timeline_post["playback"]["provider"] == "spotify"
    assert timeline_post["playback"]["provider_track_id"] == "spotify-track-1"
    assert timeline_post["playback"]["preview_url"] == "https://example.com/preview.mp3"
