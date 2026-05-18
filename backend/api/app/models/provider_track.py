from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProviderTrack(Base):
    __tablename__ = "provider_tracks"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_track_id",
            name="uq_provider_tracks_provider_track",
        ),
        Index(
            "ix_provider_tracks_track_provider",
            "track_id",
            "provider",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    track_id: Mapped[str] = mapped_column(ForeignKey("tracks.id"), index=True)
    provider: Mapped[str] = mapped_column(String(40))
    provider_track_id: Mapped[str] = mapped_column(String(160))

    title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    artist_name: Mapped[str | None] = mapped_column(String(240), nullable=True)
    album_name: Mapped[str | None] = mapped_column(String(240), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String(32), nullable=True)

    playback_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    artwork_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_playable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    playback_source: Mapped[str | None] = mapped_column(String(40), nullable=True)

    provider_metadata: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    metadata_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )

    track = relationship("Track", back_populates="provider_tracks")
