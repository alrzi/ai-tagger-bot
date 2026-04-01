"""Use case: анализ записи через ИИ."""

from __future__ import annotations

import logging
from typing import Protocol

from src.domain.entities import AnalysisResult, Entry

logger = logging.getLogger(__name__)


class EntryReader(Protocol):
    """Протокол для чтения записи."""

    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None: ...


class EntryUpdater(Protocol):
    """Протокол для обновления записи."""

    async def save(self, entry: Entry) -> Entry: ...


class EntryAnalysisService(Protocol):
    """Протокол сервиса анализа текста.

    Реализация живёт в infrastructure (OllamaEntryAnalysisService).
    Use case знает только контракт, не детали реализации.
    """

    async def analyze(self, text: str) -> AnalysisResult: ...


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

        # Получаем доменный объект — никакого парсинга здесь
        result = await self.analysis_service.analyze(entry.raw_text)

        entry.apply_analysis(result)

        return await self.updater.save(entry)
