"""Доменные сущности. Чистый Python, никаких внешних зависимостей."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ContentType(Enum):
    ARTICLE = "article"
    NOTE = "note"
    TUTORIAL = "tutorial"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AnalysisResult:
    """Результат анализа текста через ИИ. Value object."""

    summary: str
    tags: list[str]
    content_type: ContentType


@dataclass
class Entry:
    """Запись пользователя (пост, ссылка, заметка)."""

    id: Optional[int] = None
    user_id: int = 0
    url: Optional[str] = None
    title: str = ""
    raw_text: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=lambda: list[str]())
    content_type: ContentType = ContentType.UNKNOWN
    embedding: Optional[list[float]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_processed(self) -> bool:
        return bool(self.summary and self.tags)

    def apply_analysis(self, result: AnalysisResult) -> None:
        """Применяет результаты анализа к записи."""
        self.summary = result.summary
        self.tags = result.tags
        self.content_type = result.content_type

    def get_text_for_embedding(self) -> str:
        """Возвращает текст для генерации эмбеддинга."""
        text = self.summary or self.raw_text
        return text[:2000]
