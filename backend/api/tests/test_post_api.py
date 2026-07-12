from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.post import Post
from app.models.provider_track import ProviderTrack
from app.models.track import Track
from app.models.user import User


def test_create_and_list_posts(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="spotify-track-1",
        title="Test Track",
        artist_name="Test Artist",
    )
    db_session.add_all([user, track, provider_track])
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(provider_track)
    token = create_access_token(subject=user.id)

    create_response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider": "spotify",
            "provider_track_id": "spotify-track-1",
            "caption": "first post",
        },
    )

    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["user_id"] == user.id
    assert created_post["track_id"] == track.id
    assert created_post["source_provider_track_id"] == provider_track.id

    list_response = client.get("/posts")

    assert list_response.status_code == 200
    data = list_response.json()
    posts = data["items"]
    assert len(posts) == 1
    assert posts[0]["id"] == created_post["id"]
    assert posts[0]["playback"]["provider"] == "spotify"
    assert posts[0]["playback"]["provider_track_id"] == "spotify-track-1"
    assert data["next_before"] == posts[0]["created_at"]


def test_list_posts_includes_playback_when_track_exists(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="spotify-track-1",
        title="Test Track",
        artist_name="Test Artist",
        album_name="Test Album",
        duration_ms=180000,
        artwork_url="https://example.com/artwork.jpg",
        provider_url="https://open.spotify.com/track/spotify-track-1",
        preview_url="https://example.com/preview.mp3",
        playback_id="spotify-track-1",
        is_playable=True,
    )
    db_session.add_all([user, track, provider_track])
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    create_response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider": "spotify",
            "provider_track_id": "spotify-track-1",
            "caption": "track with playback",
        },
    )

    assert create_response.status_code == 201

    list_response = client.get("/posts")

    assert list_response.status_code == 200
    data = list_response.json()
    posts = data["items"]
    assert len(posts) == 1
    assert posts[0]["playback"] == {
        "provider": "spotify",
        "provider_track_id": "spotify-track-1",
        "title": "Test Track",
        "artist_name": "Test Artist",
        "album_name": "Test Album",
        "duration_ms": 180000,
        "artwork_url": "https://example.com/artwork.jpg",
        "provider_url": "https://open.spotify.com/track/spotify-track-1",
        "preview_url": "https://example.com/preview.mp3",
        "playback_id": "spotify-track-1",
        "is_playable": True,
        "playback_mode": "preview",
    }
    assert data["next_before"] == posts[0]["created_at"]


def test_list_posts_marks_apple_music_playback_as_external(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    provider_track = ProviderTrack(
        track=track,
        provider="apple_music",
        provider_track_id="apple-track-1",
        title="Apple Track",
        artist_name="Apple Artist",
        provider_url="https://music.apple.com/song/apple-track-1",
        preview_url="https://audio-ssl.itunes.apple.com/preview",
        playback_id="apple-track-1",
        is_playable=True,
    )
    post = Post(
        user=user,
        track=track,
        source_provider_track=provider_track,
        item_type="track",
        caption="apple external only",
    )
    db_session.add_all([user, track, provider_track, post])
    db_session.commit()

    response = client.get("/posts")

    assert response.status_code == 200
    playback = response.json()["items"][0]["playback"]
    assert playback["provider"] == "apple_music"
    assert playback["playback_mode"] == "external"


def test_list_posts_marks_missing_preview_as_external(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="spotify-track-1",
        title="Spotify Track",
        artist_name="Spotify Artist",
        provider_url="https://open.spotify.com/track/spotify-track-1",
        preview_url=None,
        playback_id="spotify-track-1",
        is_playable=True,
    )
    post = Post(
        user=user,
        track=track,
        source_provider_track=provider_track,
        item_type="track",
        caption="external only",
    )
    db_session.add_all([user, track, provider_track, post])
    db_session.commit()

    response = client.get("/posts")

    assert response.status_code == 200
    playback = response.json()["items"][0]["playback"]
    assert playback["provider"] == "spotify"
    assert playback["playback_mode"] == "external"


def test_list_posts_filters_by_before_cursor(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    newer_provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="newer-track",
    )
    older_provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="older-track",
    )
    newer_post = Post(
        user=user,
        track=track,
        source_provider_track=newer_provider_track,
        item_type="track",
        caption="newer post",
        created_at=datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc),
    )
    older_post = Post(
        user=user,
        track=track,
        source_provider_track=older_provider_track,
        item_type="track",
        caption="older post",
        created_at=datetime(2026, 5, 17, 10, 0, tzinfo=timezone.utc),
    )
    db_session.add_all(
        [
            user,
            track,
            newer_provider_track,
            older_provider_track,
            newer_post,
            older_post,
        ]
    )
    db_session.commit()

    response = client.get(
        "/posts",
        params={"before": "2026-05-17T11:00:00+00:00"},
    )

    assert response.status_code == 200
    data = response.json()
    posts = data["items"]
    assert len(posts) == 1
    assert posts[0]["id"] == older_post.id
    assert posts[0]["caption"] == "older post"
    assert data["next_before"] == posts[0]["created_at"]


def test_create_post_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/posts",
        json={
            "provider": "spotify",
            "provider_track_id": "spotify-track-1",
        },
    )

    assert response.status_code == 401


def test_create_post_rejects_invalid_payload(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider": "spotify",
        },
    )

    assert response.status_code == 422


def test_create_post_returns_404_when_provider_track_missing(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider": "spotify",
            "provider_track_id": "missing-track",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Provider track not found"}
