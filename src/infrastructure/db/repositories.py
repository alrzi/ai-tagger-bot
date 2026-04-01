"""Реализация EntryRepository через SQLAlchemy + pgvector."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import ContentType, Entry
from src.infrastructure.db.models import EntryModel


class PostgresEntryRepository:
    """Репозиторий записей на PostgreSQL + pgvector."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entry: Entry) -> Entry:
        model = EntryModel(
            user_id=entry.user_id,
            url=entry.url,
            title=entry.title,
            raw_text=entry.raw_text,
            summary=entry.summary,
            tags=entry.tags,
            content_type=entry.content_type.value,
            embedding=entry.embedding,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, entry_id: int, user_id: int) -> Optional[Entry]:
        stmt = select(EntryModel).where(
            EntryModel.id == entry_id,
            EntryModel.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]:
        stmt = (
            select(EntryModel)
            .where(EntryModel.user_id == user_id)
            .order_by(EntryModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def search_by_vector(
        self, user_id: int, query_vector: list[float], limit: int = 5
    ) -> list[tuple[Entry, float]]:
        query = text(
            """
            SELECT *, 1 - (embedding <=> :vec) AS similarity
            FROM entries
            WHERE user_id = :uid AND embedding IS NOT NULL
            ORDER BY embedding <=> :vec
            LIMIT :lim
            """
        )
        result = await self.session.execute(
            query,
            {"vec": str(query_vector), "uid": user_id, "lim": limit},
        )
        rows = result.fetchall()
        results: list[tuple[Entry, float]] = []
        for row in rows:
            entry = Entry(
                id=row.id,
                user_id=row.user_id,
                url=row.url,
                title=row.title or "",
                raw_text=row.raw_text or "",
                summary=row.summary or "",
                tags=list(row.tags) if row.tags else [],
                content_type=ContentType(row.content_type) if row.content_type else ContentType.UNKNOWN,
                embedding=list(row.embedding) if row.embedding else None,
                created_at=row.created_at,
            )
            results.append((entry, float(row.similarity)))
        return results

    async def search_by_tags(
        self, user_id: int, tags: list[str], limit: int = 10
    ) -> list[Entry]:
        stmt = (
            select(EntryModel)
            .where(
                EntryModel.user_id == user_id,
                EntryModel.tags.overlap(tags),
            )
            .order_by(EntryModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def delete(self, entry_id: int, user_id: int) -> bool:
        model = await self.session.get(EntryModel, entry_id)
        if model is None or model.user_id != user_id:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def update_embedding(self, entry_id: int, embedding: list[float]) -> None:
        """Обновляет эмбеддинг записи."""
        model = await self.session.get(EntryModel, entry_id)
        if model is None:
            return
        model.embedding = embedding
        await self.session.commit()

    @staticmethod
    def _to_domain(model: EntryModel) -> Entry:
        return Entry(
            id=model.id,
            user_id=model.user_id,
            url=model.url,
            title=model.title or "",
            raw_text=model.raw_text or "",
            summary=model.summary or "",
            tags=list(model.tags) if model.tags else [],
            content_type=ContentType(model.content_type) if model.content_type else ContentType.UNKNOWN,
            embedding=list(model.embedding) if model.embedding else None,
            created_at=model.created_at,
        )
