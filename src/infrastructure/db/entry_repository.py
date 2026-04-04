"""Реализация EntryRepository через SQLAlchemy + pgvector."""

from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Entry
from src.domain.interfaces import TagRepository
from src.infrastructure.db.models import EntryModel


class PostgresEntryRepository:
    """Репозиторий записей на PostgreSQL + pgvector."""

    def __init__(self, session: AsyncSession, tag_repository: TagRepository) -> None:
        self.session = session
        self.tag_repository = tag_repository

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

        entry = self._model_to_entry(model)
        tags_map = await self.tag_repository.get_tags_for_entries([entry_id])
        entry.tags = tags_map.get(entry_id, [])
        return entry

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]:
        stmt = (
            select(EntryModel)
            .where(EntryModel.user_id == user_id)
            .order_by(EntryModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        entries = [self._model_to_entry(m) for m in models]

        entry_ids = [entry.id for entry in entries if entry.id is not None]
        tags_map = await self.tag_repository.get_tags_for_entries(entry_ids)

        for entry in entries:
            if entry.id is not None:
                entry.tags = tags_map.get(entry.id, [])

        return entries


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
            category_position=entry.category_position,
            url=entry.url,
            title=entry.title,
            raw_text=entry.raw_text,
            summary=entry.summary,
            embedding=entry.embedding,
        )

    def _update_model_from_entry(self, model: EntryModel, entry: Entry) -> None:
        model.summary = entry.summary
        model.category_position = entry.category_position
        model.embedding = entry.embedding

    def _model_to_entry(self, model: EntryModel) -> Entry:
        return Entry(
            id=model.id,
            user_id=model.user_id,
            category_position=model.category_position,
            url=model.url,
            title=model.title or "",
            raw_text=model.raw_text or "",
            summary=model.summary or "",
            tags=[],
            embedding=self._parse_embedding(model.embedding),
            is_read=model.is_read,
            created_at=model.created_at,
        )

    def _row_to_entry(self, row: Row) -> tuple[Entry, float]:  # type: ignore[type-arg]
        data = row._mapping
        embedding = self._parse_embedding(data.get("embedding"))
        entry = Entry(
            id=data["id"],
            user_id=data["user_id"],
            category_position=data.get("category_position", 0),
            url=data.get("url"),
            title=data.get("title") or "",
            raw_text=data.get("raw_text") or "",
            summary=data.get("summary") or "",
            tags=[],
            embedding=embedding,
            created_at=data["created_at"],
        )
        similarity = data.get("similarity", 0.0)
        return entry, float(similarity)

    @staticmethod
    def _parse_embedding(embedding: list[float] | str | None) -> list[float] | None:
        if embedding is None:
            return None
        if isinstance(embedding, str):
            embedding = json.loads(embedding)
        return [float(x) for x in embedding]  # type: ignore[union-attr]
