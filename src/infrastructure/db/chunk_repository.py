"""Реализация ChunkRepository через PostgreSQL."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces import ChunkRepository
from src.infrastructure.db.models import ChunkModel


class PostgresChunkRepository(ChunkRepository):
    """Репозиторий чанков на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entry_id: int, text: str, embedding: list[float], position: int) -> None:
        """Создать чанк."""
        model = ChunkModel(
            entry_id=entry_id,
            text=text,
            embedding=embedding,
            position=position,
        )
        self.session.add(model)

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
        await self.session.flush()

    async def delete_by_entry_id(self, entry_id: int) -> None:
        """Удалить все чанки для записи."""
        await self.session.execute(
            ChunkModel.delete().where(ChunkModel.entry_id == entry_id)  # type: ignore[attr-defined]
        )
        await self.session.flush()
