"""Use case: анализ записи через ИИ."""

from __future__ import annotations

import logging

from src.domain.entities import Entry
from src.domain.interfaces import EntryAnalysisService, EntryReader, EntryUpdater

logger = logging.getLogger(__name__)


class AnalyzeEntryUseCase:
    """Сценарий: анализ записи через ИИ → summary + tags."""

    def __init__(
        self,
        reader: EntryReader,
        updater: EntryUpdater,
        analysis_service: EntryAnalysisService,
    ) -> None:
        self.reader = reader
        self.updater = updater
        self.analysis_service = analysis_service

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        entry = await self.reader.get_by_id(entry_id, user_id)
        if entry is None:
            raise ValueError(f"Запись {entry_id} не найдена")

        if not entry.raw_text.strip():
            raise ValueError("Нет текста для анализа")

        result = await self.analysis_service.analyze(entry.raw_text)

        entry.apply_analysis(result)

        return await self.updater.save(entry)
