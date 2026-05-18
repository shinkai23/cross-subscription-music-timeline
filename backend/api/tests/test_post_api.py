from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.post import Post
from app.models.track import Track
from app.models.user import User


def test_create_and_list_posts(client: TestClient, db_session: Session) -> None:
    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    create_response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "item_type": "track",
            "source_provider": "spotify",
            "source_item_id": "spotify-track-1",
            "caption": "first post",
        },
    )

    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["user_id"] == user.id
    assert created_post["source_provider"] == "spotify"
    assert created_post["source_item_id"] == "spotify-track-1"

    list_response = client.get("/posts")

    assert list_response.status_code == 200
    data = list_response.json()
    posts = data["items"]
    assert len(posts) == 1
    assert posts[0]["id"] == created_post["id"]
    assert posts[0]["playback"] is None
    assert data["next_before"] == posts[0]["created_at"]


def test_list_posts_includes_playback_when_track_exists(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    track = Track(
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
    db_session.add_all([user, track])
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)

    create_response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "item_type": "track",
            "source_provider": "spotify",
            "source_item_id": "spotify-track-1",
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
    }
    assert data["next_before"] == posts[0]["created_at"]


def test_list_posts_filters_by_before_cursor(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(display_name="Test User", handle="test-user")
    newer_post = Post(
        user=user,
        item_type="track",
        source_provider="spotify",
        source_item_id="newer-track",
        caption="newer post",
        created_at=datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc),
    )
    older_post = Post(
        user=user,
        item_type="track",
        source_provider="spotify",
        source_item_id="older-track",
        caption="older post",
        created_at=datetime(2026, 5, 17, 10, 0, tzinfo=timezone.utc),
    )
    db_session.add_all([user, newer_post, older_post])
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
            "item_type": "track",
            "source_provider": "spotify",
            "source_item_id": "spotify-track-1",
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
            "item_type": "track",
            "source_provider": "spotify",
        },
    )

    assert response.status_code == 422
