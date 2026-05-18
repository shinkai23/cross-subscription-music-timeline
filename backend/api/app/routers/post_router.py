from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.repositories.provider_track_repository import ProviderTrackRepository
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostCreate, PostListRead, PostRead
from app.services.post_service import PostService, ProviderTrackNotFoundError


router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(
        repository=PostRepository(db),
        provider_track_repository=ProviderTrackRepository(db),
    )


@router.get("", response_model=PostListRead)
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
    try:
        return service.create_post(post_in, current_user=current_user)
    except ProviderTrackNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider track not found",
        ) from exc
