"""Use case: анализ записи через ИИ."""

from __future__ import annotations

import logging

from src.domain.entities import Entry
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.interfaces import (
    CategoryRepository,
    EmbeddingGenerator,
    EntryAnalysisService,
    EntryRepository,
)
from src.infrastructure.ai.analysis import OllamaEntryAnalysisService

logger = logging.getLogger(__name__)


class AnalyzeEntryInteractor:
    """Сценарий: анализ записи через ИИ → summary + tags + embedding + категории."""

    def __init__(
        self,
        repository: EntryRepository,
        analysis_service: EntryAnalysisService,
        embedder: EmbeddingGenerator,
        category_repository: CategoryRepository,
    ) -> None:
        self.repository = repository
        self.analysis_service = analysis_service
        self.embedder = embedder
        self.category_repository = category_repository

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        entry = await self.repository.get_by_id(entry_id, user_id)
        if entry is None:
            raise NotFoundError(f"Запись {entry_id} не найдена")

        if not entry.raw_text.strip():
            raise ValidationError("Нет текста для анализа")

        # Анализ через ИИ
        result = await self.analysis_service.analyze(entry.raw_text)
        entry.apply_analysis(result)

        # Категоризация тегов (если сервис поддерживает)
        if isinstance(self.analysis_service, OllamaEntryAnalysisService) and entry.tags:
            categories = await self.category_repository.get_categories(user_id)
            tag_positions = await self.analysis_service.categorize_tags(
                entry.tags, categories.names
            )
            for tag, position in tag_positions.items():
                await self.category_repository.cache_position(user_id, tag, position)

        # Эмбеддинг (бизнес-логика в Entity)
        text_to_embed = entry.get_text_for_embedding()
        embedding = await self.embedder.embed(text_to_embed)
        entry.embedding = embedding

        return await self.repository.save(entry)
