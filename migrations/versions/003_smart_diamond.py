"""add user_categories, tag_category_cache, is_read

Revision ID: 003_smart_diamond
Revises: 002_embedding_4096
Create Date: 2026-04-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003_smart_diamond"
down_revision: Union[str, None] = "002_embedding_4096"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Категории пользователя (5 категорий для ромба)
    op.create_table(
        "user_categories",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "position"),
    )

    # Кэш маппинга тег → категория
    op.create_table(
        "tag_category_cache",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("tag", sa.String(100), nullable=False),
        sa.Column("category_position", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "tag"),
    )
    op.create_index(
        "idx_tag_category_cache_user", "tag_category_cache", ["user_id"]
    )

    # Флаг прочитанности для /review
    op.add_column(
        "entries",
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("idx_entries_is_read", "entries", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_index("idx_entries_is_read", table_name="entries")
    op.drop_column("entries", "is_read")
    op.drop_index("idx_tag_category_cache_user", table_name="tag_category_cache")
    op.drop_table("tag_category_cache")
    op.drop_table("user_categories")
