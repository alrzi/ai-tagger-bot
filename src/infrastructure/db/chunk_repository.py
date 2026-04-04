"""Реализация ChunkRepository через PostgreSQL."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces import ChunkRepository
from src.infrastructure.db.models import ChunkModel


class PostgresChunkRepository(ChunkRepository):
    """Репозиторий чанков на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_chunks(self, entry_id: int, chunks: list[tuple[str, list[float]]]) -> None:
        """Массовое сохранение чанков для записи."""
        models = []
        for position, (text, embedding) in enumerate(chunks):
            models.append(ChunkModel(
                entry_id=entry_id,
                text=text,
                embedding=embedding,
                position=position,
            ))
        
        self.session.add_all(models)
        await self.session.commit()

    async def delete_by_entry_id(self, entry_id: int) -> None:
        """Удалить все чанки для записи."""
        from sqlalchemy import delete

        await self.session.execute(
            delete(ChunkModel).where(ChunkModel.entry_id == entry_id)
        )
        await self.session.commit()
