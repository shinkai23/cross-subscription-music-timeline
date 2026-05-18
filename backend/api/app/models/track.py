from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
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


class Track(Base):
    __tablename__ = "tracks"
    __table_args__ = (
        UniqueConstraint("provider", "provider_track_id", name="uq_tracks_provider_track"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    provider: Mapped[str] = mapped_column(String(40))
    provider_track_id: Mapped[str] = mapped_column(String(160))
    isrc: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(240))
    artist_name: Mapped[str] = mapped_column(String(240))
    album_name: Mapped[str | None] = mapped_column(String(240), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    artwork_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    playback_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_playable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    provider_metadata: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    provider_tracks = relationship(
        "ProviderTrack",
        back_populates="track",
    )


class TrackMatch(Base):
    __tablename__ = "track_matches"
    __table_args__ = (
        Index(
            "ix_track_matches_source_target",
            "source_provider",
            "source_track_id",
            "target_provider",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    source_provider: Mapped[str] = mapped_column(String(40))
    source_track_id: Mapped[str] = mapped_column(String(160))
    target_provider: Mapped[str] = mapped_column(String(40))
    target_track_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    reason: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
