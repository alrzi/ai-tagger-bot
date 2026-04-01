"""Use case: анализ записи через ИИ."""

from __future__ import annotations

import json
import logging
import re
from typing import Protocol

from src.domain.entities import ContentType, Entry
from src.infrastructure.ai.prompts import ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class EntryReader(Protocol):
    """Протокол для чтения записи."""

    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None: ...


class EntryUpdater(Protocol):
    """Протокол для обновления записи."""

    async def save(self, entry: Entry) -> Entry: ...


class AIClient(Protocol):
    """Протокол для ИИ-клиента."""

    async def generate(self, prompt: str) -> str: ...


class AnalyzeEntryUseCase:
    """Сценарий: анализ записи через Ollama → summary + tags."""

    def __init__(
        self,
        reader: EntryReader,
        updater: EntryUpdater,
        ai_client: AIClient,
    ) -> None:
        self.reader = reader
        self.updater = updater
        self.ai_client = ai_client

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        entry = await self.reader.get_by_id(entry_id, user_id)
        if entry is None:
            raise ValueError(f"Запись {entry_id} не найдена")

        if not entry.raw_text.strip():
            raise ValueError("Нет текста для анализа")

        prompt = ANALYSIS_PROMPT.format(content=entry.raw_text[:3000])
        response = await self.ai_client.generate(prompt)

        # Извлекаем JSON из ответа (модель может добавить текст вокруг)
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
            except json.JSONDecodeError:
                logger.warning("Не удалось распарсить JSON от ИИ: %s", response[:200])
                data = {
                    "summary": "Не удалось проанализировать",
                    "tags": [],
                    "type": "unknown",
                }
        else:
            logger.warning("JSON не найден в ответе ИИ: %s", response[:200])
            data = {
                "summary": "Не удалось проанализировать",
                "tags": [],
                "type": "unknown",
            }

        entry.summary = data.get("summary", "")
        entry.tags = data.get("tags", [])
        entry.content_type = ContentType(data.get("type", "unknown"))

        return await self.updater.save(entry)
