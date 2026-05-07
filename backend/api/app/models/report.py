from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    reporter_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[str | None] = mapped_column(
        ForeignKey("posts.id"),
        nullable=True,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(String(40))
    target_id: Mapped[str] = mapped_column(String(160), index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    post = relationship("Post", back_populates="reports")
