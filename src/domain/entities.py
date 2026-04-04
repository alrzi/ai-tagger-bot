"""Доменные сущности. Чистый Python, никаких внешних зависимостей."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass(frozen=True)
class AnalysisResult:
    """Результат анализа текста через ИИ. Value object."""

    summary: str
    tags: list[str]
    category: str


@dataclass
class Entry:
    """Запись пользователя (пост, ссылка, заметка)."""

    id: Optional[int] = None
    user_id: int = 0
    category_position: int = 0
    url: Optional[str] = None
    title: str = ""
    raw_text: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=lambda: list[str]())
    embedding: Optional[list[float]] = None
    is_read: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_processed(self) -> bool:
        return bool(self.summary and self.tags)

    def apply_analysis(self, result: AnalysisResult) -> None:
        """Применяет результаты анализа к записи."""
        self.summary = result.summary
        self.tags = result.tags

    def get_text_for_embedding(self) -> str:
        """Возвращает текст для генерации эмбеддинга."""
        parts = []
        if self.category_position is not None:
            parts.append(str(self.category_position))
        if self.title:
            parts.append(self.title)
        if self.summary:
            parts.append(self.summary)
        return " ".join(parts)[:2000]


@dataclass(frozen=True)
class UserCategories:
    """5 категорий пользователя для ромба."""

    user_id: int
    names: list[str]

    def __post_init__(self) -> None:
        if len(self.names) != 5:
            raise ValueError(f"Должно быть ровно 5 категорий, получено {len(self.names)}")

    @staticmethod
    def defaults(user_id: int) -> "UserCategories":
        """Категории по умолчанию."""
        return UserCategories(
            user_id=user_id,
            names=["Hard Skills", "Soft Skills", "Ideas", "Health", "Finance"],
        )
