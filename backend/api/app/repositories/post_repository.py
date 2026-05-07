from sqlalchemy import select
from sqlalchemy.orm import Session

import app.db.base  # noqa: F401
from app.models.post import Post
from app.schemas.post_schema import PostCreate


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_posts(self, limit: int = 50, offset: int = 0) -> list[Post]:
        statement = select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(statement).all())

    def create_post(self, post_in: PostCreate) -> Post:
        post = Post(**post_in.model_dump())
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
