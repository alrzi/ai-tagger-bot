"""Синхронизация тегов записи."""

from __future__ import annotations

from src.domain.interfaces import TagRepository
from src.domain.tag_normalizer import TagNormalizer
from src.application import log_use_case


class SyncEntryTags:
    """Синхронизировать теги для записи.
    
    Содержит всю бизнес логику операции, не знает про реализацию репозитория.
    """

    def __init__(self, tag_repository: TagRepository):
        self._tag_repository = tag_repository

    async def __call__(self, entry_id: int, user_id: int, tags: list[str]) -> None:
        log_use_case.info(f"🔖 Начинаю SyncEntryTags | entry_id={entry_id}, тегов={len(tags)}")
        normalized_tags = TagNormalizer.normalize_list(tags)

        if not normalized_tags:
            log_use_case.info(f"ℹ️ Нет нормализованных тегов | entry_id={entry_id}")
            await self._tag_repository.replace_entry_tags(entry_id, [])
            return

        existing = await self._tag_repository.find_by_normalized_names(
            user_id,
            list(normalized_tags.keys())
        )

        new_tags = [
            (normalized, original)
            for normalized, original in normalized_tags.items()
            if normalized not in existing
        ]

        if new_tags:
            created = await self._tag_repository.create_many(user_id, new_tags)
            existing.update(created)

        tag_ids = [existing[name] for name in normalized_tags]

        await self._tag_repository.replace_entry_tags(entry_id, tag_ids)
        log_use_case.info(f"✅ Теги синхронизированы | entry_id={entry_id}, тегов={len(tag_ids)}")
