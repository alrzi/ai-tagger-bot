"""Сервис анализа текста через Ollama.

Реализует протокол EntryAnalysisService из use case-слоя.
Парсинг JSON делегирован OllamaClient.generate_structured().
"""

from __future__ import annotations

import logging

from src.domain.entities import AnalysisResult, UserCategories
from src.domain.exceptions import AIServiceError
from src.domain.interfaces import AIClient
from src.infrastructure.ai.prompts import ANALYSIS_PROMPT
from src.infrastructure.ai.schemas import AIAnalysisDTO

logger = logging.getLogger(__name__)


class OllamaEntryAnalysisService:
    """Анализ текста записи через Ollama.

    Знает о специфике Ollama: формат промптов, маппинг DTO → домен.
    Парсинг JSON делегирован клиенту через generate_structured().
    """

    def __init__(self, ai_client: AIClient) -> None:
        self.ai_client = ai_client

    async def analyze(self, text: str, categories: UserCategories, existing_tags: list[str]) -> AnalysisResult:
        """Анализирует текст и возвращает доменный результат.

        Args:
            text: Текст записи для анализа
            categories: 5 категорий пользователя
            existing_tags: Список существующих тегов пользователя для подсказки

        Raises:
            AIServiceError: Если не удалось получить или распарсить ответ модели.
        """
        prompt = ANALYSIS_PROMPT.format(
            content=text[:4000],
            categories="\n".join(f"- {name}" for name in categories.names),
            existing_tags=", ".join(existing_tags),
        )

        try:
            dto = await self.ai_client.generate_structured(prompt, AIAnalysisDTO)
        except Exception as exc:
            logger.warning("Ошибка анализа ИИ: %s", exc)
            raise AIServiceError("Не удалось разобрать ответ нейросети") from exc

        summary, tags, category = dto.to_domain()

        return AnalysisResult(
            summary=summary,
            tags=tags,
            category=category,
        )
