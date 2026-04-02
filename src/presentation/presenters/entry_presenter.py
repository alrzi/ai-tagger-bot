"""Presenter для записей — логика отображения (эмодзи, обрезка, форматирование)."""

from __future__ import annotations

from typing import Protocol

from src.domain.dto import EntryDTO


class EntryPresenterProtocol(Protocol):
    """Интерфейс для форматирования записей."""

    def format_list(self, entries: list[EntryDTO]) -> str: ...
    def format_search(
        self, results: list[tuple[EntryDTO, float]]
    ) -> tuple[str, list[int]]: ...
    def format_full(self, entry: EntryDTO) -> str: ...


class TelegramEntryPresenter:
    """Telegram-реализация presenter'а."""

    _SUMMARY_LIMIT = 100
    _SEARCH_SUMMARY_LIMIT = 200

    def format_list(self, entries: list[EntryDTO]) -> str:
        lines = [f"📋 Последние {len(entries)} записей:"]
        for entry in entries:
            tags = self._format_tags(entry.tags)
            summary = self._truncate(entry.summary or entry.raw_text, self._SUMMARY_LIMIT)
            lines.append(f"🆔 {entry.id}\n📝 {summary}\n🏷 {tags}")
        return "\n\n".join(lines)

    def format_search(
        self, results: list[tuple[EntryDTO, float]]
    ) -> tuple[str, list[int]]:
        lines = [f"🔍 Найдено {len(results)} записей:"]
        entry_ids: list[int] = []
        for i, (entry, similarity) in enumerate(results, 1):
            tags = self._format_tags(entry.tags)
            summary = self._truncate(
                entry.summary or entry.raw_text, self._SEARCH_SUMMARY_LIMIT
            )
            lines.append(
                f"{i}. 🆔 {entry.id} ({similarity:.0%})\n"
                f"📝 {summary}\n"
                f"🏷 {tags}"
            )
            if entry.id is not None:
                entry_ids.append(entry.id)
        return "\n\n".join(lines), entry_ids

    def format_full(self, entry: EntryDTO) -> str:
        tags = self._format_tags(entry.tags)
        parts = [
            f"📝 Запись #{entry.id}",
            "",
            entry.raw_text,
            "",
            f"🏷 {tags}",
            f"📂 Тип: {entry.content_type}",
        ]
        if entry.url:
            parts.append(f"🔗 {entry.url}")
        if entry.summary:
            parts.extend(["", "📋 Резюме:", entry.summary])
        return "\n".join(parts)

    @staticmethod
    def _format_tags(tags: list[str]) -> str:
        return " ".join(f"#{t}" for t in tags) or "без тегов"

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + "..."
