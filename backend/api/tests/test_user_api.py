from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.service_account import ServiceAccount


def test_create_user(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "display_name": "Test User",
            "handle": "test-user",
            "primary_provider": "spotify",
        },
    )

    assert response.status_code == 201
    user = response.json()
    assert user["display_name"] == "Test User"
    assert user["handle"] == "test-user"
    assert user["primary_provider"] == "spotify"
    assert "id" in user


def test_create_user_rejects_duplicate_handle(client: TestClient) -> None:
    payload = {
        "display_name": "Test User",
        "handle": "test-user",
    }

    first_response = client.post("/users", json=payload)
    second_response = client.post("/users", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_read_me(client: TestClient) -> None:
    create_response = client.post(
        "/users",
        json={
            "display_name": "Test User",
            "handle": "test-user",
        },
    )
    user = create_response.json()
    token = create_access_token(subject=user["id"])

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


def test_read_me_rejects_missing_token(client: TestClient) -> None:
    response = client.get("/me")

    assert response.status_code == 401


def test_read_me_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_read_my_provider_accounts_returns_connected_accounts(
    client: TestClient,
    db_session: Session,
) -> None:
    create_response = client.post(
        "/users",
        json={
            "display_name": "Test User",
            "handle": "test-user",
        },
    )
    user = create_response.json()
    token = create_access_token(subject=user["id"])
    db_session.add(
        ServiceAccount(
            user_id=user["id"],
            provider="spotify",
            provider_user_id="spotify-user-1",
            encrypted_refresh_token="encrypted-refresh-token",
        )
    )
    db_session.commit()

    response = client.get(
        "/me/provider-accounts",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == [
        {
            "provider": "spotify",
            "provider_user_id": "spotify-user-1",
            "connected": True,
            "created_at": data["items"][0]["created_at"],
        }
    ]


def test_read_my_provider_accounts_ignores_disconnected_accounts(
    client: TestClient,
    db_session: Session,
) -> None:
    create_response = client.post(
        "/users",
        json={
            "display_name": "Test User",
            "handle": "test-user",
        },
    )
    user = create_response.json()
    token = create_access_token(subject=user["id"])
    db_session.add(
        ServiceAccount(
            user_id=user["id"],
            provider="spotify",
            provider_user_id="spotify-user-1",
            encrypted_refresh_token="encrypted-refresh-token",
            disconnected_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    )
    db_session.commit()

    response = client.get(
        "/me/provider-accounts",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_read_my_provider_accounts_rejects_missing_token(client: TestClient) -> None:
    response = client.get("/me/provider-accounts")

    assert response.status_code == 401
