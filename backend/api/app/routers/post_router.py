from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.repositories.post_repository import PostRepository
from app.repositories.track_repository import TrackRepository
from app.schemas.post_schema import PostCreate, PostRead
from app.services.post_service import PostService


router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(
        repository=PostRepository(db),
        track_repository=TrackRepository(db),
    )


@router.get("", response_model=list[PostRead])
def list_posts(
    limit: int = Query(default=50, ge=1, le=100),
    before: datetime | None = Query(default=None),
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(limit=limit, before=before)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    return service.create_post(post_in, current_user=current_user)
