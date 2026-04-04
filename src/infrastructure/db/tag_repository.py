"""Реализация TagRepository через PostgreSQL."""

from __future__ import annotations

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.interfaces import TagRepository
from src.infrastructure.db.models import EntryTagModel, TagModel


class PostgresTagRepository(TagRepository):
    """Репозиторий тегов на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_user_tags(self, user_id: int) -> list[str]:
        """Получить все теги пользователя."""
        result = await self.session.execute(
            select(TagModel.name)
            .where(TagModel.user_id == user_id)
            .order_by(TagModel.name)
        )
        return list(result.scalars().all())

    async def find_by_normalized_names(self, user_id: int, normalized_names: list[str]) -> dict[str, int]:
        """Получить ID тегов по нормализованным именам."""
        result = await self.session.execute(
            select(TagModel.normalized_name, TagModel.id)
            .where(
                TagModel.user_id == user_id,
                TagModel.normalized_name.in_(normalized_names)
            )
        )
        return {str(row[0]): int(row[1]) for row in result.all()}

    async def create_many(self, user_id: int, tags: list[tuple[str, str]]) -> dict[str, int]:
        """Массово создать теги, обработав конфликты. Возвращает {normalized_name: id}."""
        if not tags:
            return {}

        from sqlalchemy.dialects.postgresql import insert

        stmt = insert(TagModel).values([
            {"user_id": user_id, "name": name, "normalized_name": normalized}
            for normalized, name in tags
        ])
        stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "normalized_name"])
        stmt = stmt.returning(TagModel.normalized_name, TagModel.id)
        
        result = await self.session.execute(stmt)
        return {str(row[0]): int(row[1]) for row in result.all()}

    async def replace_entry_tags(self, entry_id: int, tag_ids: list[int]) -> None:
        """Атомарно заменить все теги записи на новые."""
        async with self.session.begin_nested():
            await self.session.execute(
                delete(EntryTagModel).where(EntryTagModel.entry_id == entry_id)
            )

            if tag_ids:
                await self.session.execute(
                    insert(EntryTagModel),
                    [{"entry_id": entry_id, "tag_id": tag_id} for tag_id in tag_ids]
                )

    async def get_tags_for_entries(self, entry_ids: list[int]) -> dict[int, list[str]]:
        """
        Подгружает теги для списка записей за один SQL запрос.
        Решает N+1 проблему при загрузке списка записей.
        Автоматически разбивает на батчи при >1000 записей.
        """
        match entry_ids:
            case []:
                return {}
            case ids if len(ids) > 1000:
                mid = len(ids) // 2
                left = await self.get_tags_for_entries(ids[:mid])
                right = await self.get_tags_for_entries(ids[mid:])
                return left | right
            case _:
                stmt = (
                    select(EntryTagModel.entry_id, TagModel.name)
                    .join(TagModel, EntryTagModel.tag_id == TagModel.id)
                    .where(EntryTagModel.entry_id.in_(entry_ids))
                    .order_by(EntryTagModel.entry_id, TagModel.name)
                )
                result = await self.session.execute(stmt)

                tags_map: dict[int, list[str]] = {}
                for entry_id, tag_name in result.tuples():
                    if entry_id not in tags_map:
                        tags_map[entry_id] = []
                    tags_map[entry_id].append(tag_name)

                return tags_map
