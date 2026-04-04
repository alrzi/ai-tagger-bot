"""Внутренние DTO для парсинга ответов от Ollama.

Эти DTO не экспортируются за пределы infrastructure-слоя.
Use case работает только с доменными объектами (AnalysisResult).
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class AIAnalysisDTO(BaseModel):
    """DTO для парсинга JSON-ответа от модели анализа.

    Живёт только в infrastructure-слоя. Через to_domain()
    маппится в доменный AnalysisResult.
    """

    summary: str | list[str]
    tags: list[str] | str
    category: str

    @field_validator("summary", mode="before")
    def clean_summary(cls, v: str | list[str]) -> str:
        """Модель может вернуть summary как список строк."""
        if isinstance(v, list):
            return " ".join(str(s) for s in v)
        return v

    @field_validator("tags", mode="before")
    def clean_tags(cls, v: list[str] | str) -> list[str]:
        """Модель может вернуть tags как строку через запятую."""
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v

    def to_domain(self) -> tuple[str, list[str], str]:
        """Маппинг в кортеж для создания доменного AnalysisResult.

        Возвращает (summary, tags, category).
        Не импортирует доменные типы, чтобы не создавать циклических зависимостей.
        """
        return (
            self.summary if isinstance(self.summary, str) else str(self.summary),
            self.tags if isinstance(self.tags, list) else [str(self.tags)],
            self.category,
        )
