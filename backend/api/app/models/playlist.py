from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Playlist(Base):
    __tablename__ = "playlists"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_playlist_id",
            name="uq_playlists_provider_playlist",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    provider: Mapped[str] = mapped_column(String(40))
    provider_playlist_id: Mapped[str] = mapped_column(String(160))
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    provider_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    items = relationship("PlaylistItem", back_populates="playlist")


class PlaylistItem(Base):
    __tablename__ = "playlist_items"
    __table_args__ = (
        UniqueConstraint("playlist_id", "position", name="uq_playlist_items_position"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    playlist_id: Mapped[str] = mapped_column(ForeignKey("playlists.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    track_id: Mapped[str] = mapped_column(ForeignKey("tracks.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    playlist = relationship("Playlist", back_populates="items")
