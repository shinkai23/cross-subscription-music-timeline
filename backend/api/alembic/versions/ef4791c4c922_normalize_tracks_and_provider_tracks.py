"""normalize tracks and provider tracks

Revision ID: ef4791c4c922
Revises: f6d3b338bb76
Create Date: 2026-05-18 19:08:13.107823

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ef4791c4c922"
down_revision: str | Sequence[str] | None = "f6d3b338bb76"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tracks",
        sa.Column("canonical_source", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "tracks",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.drop_constraint(op.f("uq_tracks_provider_track"), "tracks", type_="unique")
    op.drop_column("tracks", "provider_metadata")
    op.drop_column("tracks", "playback_id")
    op.drop_column("tracks", "provider")
    op.drop_column("tracks", "preview_url")
    op.drop_column("tracks", "provider_url")
    op.drop_column("tracks", "is_playable")
    op.drop_column("tracks", "metadata_synced_at")
    op.drop_column("tracks", "provider_track_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "tracks",
        sa.Column("provider_track_id", sa.VARCHAR(length=160), nullable=True),
    )
    op.add_column(
        "tracks",
        sa.Column(
            "metadata_synced_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "tracks",
        sa.Column(
            "is_playable",
            sa.BOOLEAN(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column("tracks", sa.Column("provider_url", sa.TEXT(), nullable=True))
    op.add_column("tracks", sa.Column("preview_url", sa.TEXT(), nullable=True))
    op.add_column(
        "tracks",
        sa.Column("provider", sa.VARCHAR(length=40), nullable=True),
    )
    op.add_column(
        "tracks",
        sa.Column("playback_id", sa.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "tracks",
        sa.Column(
            "provider_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        op.f("uq_tracks_provider_track"),
        "tracks",
        ["provider", "provider_track_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.drop_column("tracks", "updated_at")
    op.drop_column("tracks", "canonical_source")
