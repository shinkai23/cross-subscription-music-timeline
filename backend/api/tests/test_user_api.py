from fastapi.testclient import TestClient

from app.core.security import create_access_token


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


def test_read_me_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
