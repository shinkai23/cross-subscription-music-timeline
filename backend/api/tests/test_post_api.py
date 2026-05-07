from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
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
    posts = list_response.json()
    assert len(posts) == 1
    assert posts[0]["id"] == created_post["id"]


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
