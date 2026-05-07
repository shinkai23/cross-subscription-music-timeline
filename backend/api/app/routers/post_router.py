from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostCreate, PostRead
from app.services.post_service import PostService


router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(PostRepository(db))


@router.get("", response_model=list[PostRead])
def list_posts(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(limit=limit, offset=offset)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    service: PostService = Depends(get_post_service),
):
    return service.create_post(post_in)
