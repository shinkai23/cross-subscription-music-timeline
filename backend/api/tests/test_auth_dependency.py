from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.dependencies.auth import get_current_subject, get_current_user
from app.dependencies.db import get_db
from app.models.user import User


def test_get_current_subject_returns_token_subject() -> None:
    app = FastAPI()

    @app.get("/subject")
    def read_subject(subject: str = Depends(get_current_subject)) -> dict[str, str]:
        return {"subject": subject}

    token = create_access_token(subject="user-1")
    client = TestClient(app)

    response = client.get(
        "/subject",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"subject": "user-1"}


def test_get_current_subject_rejects_missing_token() -> None:
    app = FastAPI()

    @app.get("/subject")
    def read_subject(subject: str = Depends(get_current_subject)) -> dict[str, str]:
        return {"subject": subject}

    client = TestClient(app)

    response = client.get("/subject")

    assert response.status_code == 401


def test_get_current_subject_rejects_invalid_token() -> None:
    app = FastAPI()

    @app.get("/subject")
    def read_subject(subject: str = Depends(get_current_subject)) -> dict[str, str]:
        return {"subject": subject}

    client = TestClient(app)

    response = client.get(
        "/subject",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_get_current_user_returns_user(
    db_session: Session,
) -> None:
    app = FastAPI()

    def override_get_db() -> Session:
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    @app.get("/me")
    def read_me(current_user: User = Depends(get_current_user)) -> dict[str, str]:
        return {"id": current_user.id, "handle": current_user.handle}

    user = User(display_name="Test User", handle="test-user")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=user.id)
    client = TestClient(app)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"id": user.id, "handle": "test-user"}


def test_get_current_user_rejects_missing_user() -> None:
    app = FastAPI()

    @app.get("/me")
    def read_me(current_user: User = Depends(get_current_user)) -> dict[str, str]:
        return {"id": current_user.id}

    token = create_access_token(subject="missing-user-id")
    client = TestClient(app)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
