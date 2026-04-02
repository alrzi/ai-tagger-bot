"""DTO для записей — чистые данные без логики отображения."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities import Entry


@dataclass(frozen=True)
class EntryDTO:
    """Чистые данные о записи для передачи между слоями."""

    id: int | None
    raw_text: str
    summary: str | None
    tags: list[str]
    url: str | None
    content_type: str

    @classmethod
    def from_entity(cls, entry: Entry) -> EntryDTO:
        """Создаёт DTO из доменной сущности."""
        return cls(
            id=entry.id,
            raw_text=entry.raw_text,
            summary=entry.summary,
            tags=entry.tags or [],
            url=entry.url,
            content_type=entry.content_type.value,
        )
