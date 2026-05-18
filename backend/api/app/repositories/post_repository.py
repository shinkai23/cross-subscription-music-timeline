from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.db.base  # noqa: F401
from app.models.post import Post


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_posts(self, limit: int = 50, before: datetime | None = None) -> list[Post]:
        statement = select(Post).order_by(Post.created_at.desc()).limit(limit)
        if before is not None:
            statement = statement.where(Post.created_at < before)
        return list(self.db.scalars(statement).all())

    def create_post(
        self,
        *,
        user_id: str,
        track_id: str,
        source_provider_track_id: str,
        caption: str | None,
        visibility: str = "public",
    ) -> Post:
        post = Post(
            user_id=user_id,
            track_id=track_id,
            source_provider_track_id=source_provider_track_id,
            item_type="track",
            caption=caption,
            visibility=visibility,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
