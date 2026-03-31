"""initial: entries table with pgvector

Revision ID: 001_initial
Revises:
Create Date: 2026-03-31
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Включаем расширение pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Создаём таблицу entries
    op.create_table(
        "entries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), server_default="", nullable=False),
        sa.Column("raw_text", sa.Text(), server_default="", nullable=False),
        sa.Column("summary", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(20),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Индексы
    op.create_index("idx_entries_user_id", "entries", ["user_id"])
    op.create_index(
        "idx_entries_embedding",
        "entries",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index(
        "idx_entries_tags",
        "entries",
        ["tags"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_table("entries")
    op.execute("DROP EXTENSION IF EXISTS vector")
