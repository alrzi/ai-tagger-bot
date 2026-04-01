"""Сервис анализа текста через Ollama.

Реализует протокол EntryAnalysisService из use case-слоя.
Парсинг JSON делегирован OllamaClient.generate_structured().
"""

from __future__ import annotations

import logging
from typing import Protocol, TypeVar

from pydantic import BaseModel

from src.domain.entities import AnalysisResult, ContentType
from src.infrastructure.ai.prompts import ANALYSIS_PROMPT
from src.infrastructure.ai.schemas import AIAnalysisDTO

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class AIClient(Protocol):
    """Протокол для ИИ-клиента."""
    
    async def generate_structured(self, prompt: str, schema: type[T]) -> T: ...


class AIServiceError(Exception):
    """Ошибка при взаимодействии с ИИ-сервисом."""


class OllamaEntryAnalysisService:
    """Анализ текста записи через Ollama.

    Знает о специфике Ollama: формат промптов, маппинг DTO → домен.
    Парсинг JSON делегирован клиенту через generate_structured().
    """

    def __init__(self, ai_client: AIClient) -> None:
        self.ai_client = ai_client

    async def analyze(self, text: str) -> AnalysisResult:
        """Анализирует текст и возвращает доменный результат.

        Raises:
            AIServiceError: Если не удалось получить или распарсить ответ модели.
        """
        prompt = ANALYSIS_PROMPT.format(content=text[:3000])

        try:
            dto = await self.ai_client.generate_structured(prompt, AIAnalysisDTO)
        except Exception as exc:
            logger.warning("Ошибка анализа ИИ: %s", exc)
            raise AIServiceError("Не удалось разобрать ответ нейросети") from exc

        summary, tags, content_type_str = dto.to_domain()

        try:
            content_type = ContentType(content_type_str)
        except ValueError:
            logger.warning("Неизвестный тип контента: %s", content_type_str)
            content_type = ContentType.UNKNOWN

        return AnalysisResult(
            summary=summary,
            tags=tags,
            content_type=content_type,
        )
