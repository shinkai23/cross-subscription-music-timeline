from fastapi.testclient import TestClient


def test_dev_login_returns_token_for_existing_handle(client: TestClient) -> None:
    create_response = client.post(
        "/users",
        json={
            "display_name": "Test User",
            "handle": "test-user",
        },
    )

    response = client.post(
        "/auth/dev-login",
        json={"handle": "test-user"},
    )

    assert create_response.status_code == 201
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_dev_login_token_can_read_me(client: TestClient) -> None:
    create_response = client.post(
        "/users",
        json={
            "display_name": "Test User",
            "handle": "test-user",
        },
    )
    user = create_response.json()
    login_response = client.post(
        "/auth/dev-login",
        json={"handle": "test-user"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


def test_dev_login_returns_404_for_missing_handle(client: TestClient) -> None:
    response = client.post(
        "/auth/dev-login",
        json={"handle": "missing-user"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_dev_login_rejects_invalid_body(client: TestClient) -> None:
    response = client.post(
        "/auth/dev-login",
        json={},
    )

    assert response.status_code == 422
