"""Use case: анализ записи через ИИ."""

from __future__ import annotations

import logging

from src.domain.entities import Entry
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.interfaces import (
    EmbeddingGenerator,
    EntryAnalysisService,
    EntryRepository,
)

logger = logging.getLogger(__name__)


class AnalyzeEntryInteractor:
    """Сценарий: анализ записи через ИИ → summary + tags + embedding."""

    def __init__(
        self,
        repository: EntryRepository,
        analysis_service: EntryAnalysisService,
        embedder: EmbeddingGenerator,
    ) -> None:
        self.repository = repository
        self.analysis_service = analysis_service
        self.embedder = embedder

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        entry = await self.repository.get_by_id(entry_id, user_id)
        if entry is None:
            raise NotFoundError(f"Запись {entry_id} не найдена")

        if not entry.raw_text.strip():
            raise ValidationError("Нет текста для анализа")

        # Анализ через ИИ
        result = await self.analysis_service.analyze(entry.raw_text)
        entry.apply_analysis(result)

        # Эмбеддинг (бизнес-логика в Entity)
        text_to_embed = entry.get_text_for_embedding()
        embedding = await self.embedder.embed(text_to_embed)
        entry.embedding = embedding

        return await self.repository.save(entry)
