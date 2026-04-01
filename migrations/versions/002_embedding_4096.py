"""change embedding to 4096 dimensions

Revision ID: 002_embedding_4096
Revises: 001_initial
Create Date: 2026-04-01
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_embedding_4096"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем старый индекс
    op.drop_index("idx_entries_embedding", table_name="entries")

    # Изменяем размерность колонки
    op.execute("ALTER TABLE entries ALTER COLUMN embedding TYPE vector(4096)")

    # Создаём новый индекс (ivfflat поддерживает 4096 измерений)
    op.execute(
        "CREATE INDEX idx_entries_embedding ON entries "
        "USING ivfflat (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("idx_entries_embedding", table_name="entries")
    op.execute("ALTER TABLE entries ALTER COLUMN embedding TYPE vector(768)")
    op.execute(
        "CREATE INDEX idx_entries_embedding ON entries "
        "USING ivfflat (embedding vector_cosine_ops)"
    )
