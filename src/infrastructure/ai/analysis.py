"""Сервис анализа текста через Ollama.

Реализует протокол EntryAnalysisService из use case-слоя.
Парсинг JSON делегирован OllamaClient.generate_structured().
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict

from src.domain.entities import AnalysisResult, ContentType
from src.domain.exceptions import AIServiceError
from src.domain.interfaces import AIClient
from src.infrastructure.ai.prompts import ANALYSIS_PROMPT, CATEGORIZE_PROMPT
from src.infrastructure.ai.schemas import AIAnalysisDTO

logger = logging.getLogger(__name__)


class TagCategoryMap(BaseModel):
    """DTO для парсинга ответа категоризации тегов."""
    
    model_config = ConfigDict(extra="allow")

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

    async def categorize_tags(
        self, tags: list[str], categories: list[str]
    ) -> dict[str, int]:
        """Определяет категорию для каждого тега.

        Args:
            tags: Список тегов для категоризации.
            categories: Список из 5 названий категорий.

        Returns:
            Словарь {тег: позиция_категории}.
        """
        if not tags:
            return {}

        categories_str = "\n".join(
            f"{i}: {name}" for i, name in enumerate(categories)
        )
        tags_str = ", ".join(tags)

        prompt = CATEGORIZE_PROMPT.format(
            categories=categories_str,
            tags=tags_str,
        )

        try:
            response = await self.ai_client.generate_structured(prompt, TagCategoryMap)
            # Преобразуем Pydantic модель в словарь
            result = response.model_dump()
            # Преобразуем строковые ключи в теги, а значения в int
            return {str(k): int(v) for k, v in result.items() if str(k) in tags}
        except Exception as exc:
            logger.warning("Ошибка категоризации тегов: %s", exc)
            # В случае ошибки возвращаем все теги в первую категорию
            return {tag: 0 for tag in tags}
