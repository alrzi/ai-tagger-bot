"""ViewModel для записей — данные, готовые к отображению."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities import Entry


@dataclass(frozen=True)
class EntryViewModel:
    """Представление записи для UI.

    Создаётся в Responder'е из доменной сущности Entry.
    Содержит только те данные, которые нужны для отображения.
    """

    id: int | None
    raw_text: str
    summary: str | None
    tags: list[str]
    url: str | None
    content_type: str

    @classmethod
    def from_entity(cls, entry: Entry) -> EntryViewModel:
        """Создаёт ViewModel из доменной сущности."""
        return cls(
            id=entry.id,
            raw_text=entry.raw_text,
            summary=entry.summary,
            tags=entry.tags or [],
            url=entry.url,
            content_type=entry.content_type.value,
        )

    @property
    def formatted_tags(self) -> str:
        """Форматирует теги: '#python #ai' или 'без тегов'."""
        return " ".join(f"#{t}" for t in self.tags) or "без тегов"

    def truncated_summary(self, limit: int = 100) -> str:
        """Обрезает summary до лимита."""
        text = self.summary or self.raw_text
        if len(text) <= limit:
            return text
        return text[:limit] + "..."
