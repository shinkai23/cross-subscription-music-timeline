"""normalize posts to canonical tracks

Revision ID: 8130855280eb
Revises: ef4791c4c922
Create Date: 2026-05-18 19:57:34.131772

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8130855280eb"
down_revision: str | Sequence[str] | None = "ef4791c4c922"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "posts",
        sa.Column("track_id", sa.String(length=36), nullable=False),
    )
    op.add_column(
        "posts",
        sa.Column("source_provider_track_id", sa.String(length=36), nullable=False),
    )
    op.drop_index(op.f("ix_posts_source_item_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_source_provider"), table_name="posts")
    op.create_index(
        op.f("ix_posts_source_provider_track_id"),
        "posts",
        ["source_provider_track_id"],
        unique=False,
    )
    op.create_index(op.f("ix_posts_track_id"), "posts", ["track_id"], unique=False)
    op.create_foreign_key(
        "fk_posts_source_provider_track_id_provider_tracks",
        "posts",
        "provider_tracks",
        ["source_provider_track_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_posts_track_id_tracks",
        "posts",
        "tracks",
        ["track_id"],
        ["id"],
    )
    op.drop_column("posts", "source_provider")
    op.drop_column("posts", "source_item_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "posts",
        sa.Column("source_item_id", sa.VARCHAR(length=160), nullable=True),
    )
    op.add_column(
        "posts",
        sa.Column("source_provider", sa.VARCHAR(length=40), nullable=True),
    )
    op.drop_constraint(
        "fk_posts_track_id_tracks",
        "posts",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_posts_source_provider_track_id_provider_tracks",
        "posts",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_posts_track_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_source_provider_track_id"), table_name="posts")
    op.create_index(
        op.f("ix_posts_source_provider"),
        "posts",
        ["source_provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_source_item_id"),
        "posts",
        ["source_item_id"],
        unique=False,
    )
    op.drop_column("posts", "source_provider_track_id")
    op.drop_column("posts", "track_id")
