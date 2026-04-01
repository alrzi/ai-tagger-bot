"""Реализация EntryRepository через SQLAlchemy + pgvector."""

from __future__ import annotations

import json
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
        if entry.id is not None:
            model = await self._get_model_by_id(entry.id)
            if model is None:
                raise ValueError(f"Запись {entry.id} не найдена")
            self._update_model_from_entry(model, entry)
        else:
            model = self._create_model(entry)
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entry(model)

    async def get_by_id(self, entry_id: int, user_id: int) -> Optional[Entry]:
        model = await self._get_model_by_id(entry_id)
        if model is None or model.user_id != user_id:
            return None
        return self._model_to_entry(model)

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]:
        stmt = (
            select(EntryModel)
            .where(EntryModel.user_id == user_id)
            .order_by(EntryModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entry(m) for m in models]

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
        return [self._row_to_entry(row) for row in result.fetchall()]

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
        return [self._model_to_entry(m) for m in models]

    async def delete(self, entry_id: int, user_id: int) -> bool:
        model = await self._get_model_by_id(entry_id)
        if model is None or model.user_id != user_id:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True

    async def update_embedding(self, entry_id: int, embedding: list[float]) -> None:
        """Обновляет эмбеддинг записи."""
        model = await self._get_model_by_id(entry_id)
        if model is None:
            return
        model.embedding = embedding
        await self.session.commit()

    # --- Private helpers ---

    async def _get_model_by_id(self, entry_id: int) -> Optional[EntryModel]:
        return await self.session.get(EntryModel, entry_id)

    def _create_model(self, entry: Entry) -> EntryModel:
        return EntryModel(
            user_id=entry.user_id,
            url=entry.url,
            title=entry.title,
            raw_text=entry.raw_text,
            summary=entry.summary,
            tags=entry.tags,
            content_type=entry.content_type.value,
            embedding=entry.embedding,
        )

    def _update_model_from_entry(self, model: EntryModel, entry: Entry) -> None:
        model.summary = entry.summary
        model.tags = entry.tags
        model.content_type = entry.content_type.value
        model.embedding = entry.embedding

    def _model_to_entry(self, model: EntryModel) -> Entry:
        return Entry(
            id=model.id,
            user_id=model.user_id,
            url=model.url,
            title=model.title or "",
            raw_text=model.raw_text or "",
            summary=model.summary or "",
            tags=self._parse_tags(model.tags),
            content_type=ContentType(model.content_type) if model.content_type else ContentType.UNKNOWN,
            embedding=self._parse_embedding(model.embedding),
            created_at=model.created_at,
        )

    def _row_to_entry(self, row: object) -> tuple[Entry, float]:
        embedding = self._parse_embedding(row.embedding)
        entry = Entry(
            id=row.id,
            user_id=row.user_id,
            url=row.url,
            title=row.title or "",
            raw_text=row.raw_text or "",
            summary=row.summary or "",
            tags=self._parse_tags(row.tags),
            content_type=ContentType(row.content_type) if row.content_type else ContentType.UNKNOWN,
            embedding=embedding,
            created_at=row.created_at,
        )
        return entry, float(row.similarity)

    @staticmethod
    def _parse_tags(tags: list[str] | None) -> list[str]:
        if tags is None:
            return []
        return [str(t) for t in tags]

    @staticmethod
    def _parse_embedding(embedding: list[float] | str | None) -> list[float] | None:
        if embedding is None:
            return None
        if isinstance(embedding, str):
            embedding = json.loads(embedding)
        return [float(x) for x in embedding]  # type: ignore[union-attr]
