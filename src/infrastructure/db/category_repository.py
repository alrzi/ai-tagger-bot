"""Реализация CategoryRepository через SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import UserCategories
from src.infrastructure.db.models import TagCategoryCacheModel, UserCategoryModel


class PostgresCategoryRepository:
    """Репозиторий категорий на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_categories(self, user_id: int) -> UserCategories:
        """Возвращает категории пользователя или значения по умолчанию."""
        stmt = (
            select(UserCategoryModel)
            .where(UserCategoryModel.user_id == user_id)
            .order_by(UserCategoryModel.position)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        if not models:
            return UserCategories.defaults(user_id)

        names = [m.name for m in models]
        return UserCategories(user_id=user_id, names=names)

    async def set_categories(self, categories: UserCategories) -> None:
        """Сохраняет категории пользователя."""
        # Удаляем старые
        await self.session.execute(
            delete(UserCategoryModel).where(
                UserCategoryModel.user_id == categories.user_id
            )
        )

        # Вставляем новые
        for position, name in enumerate(categories.names):
            model = UserCategoryModel(
                user_id=categories.user_id,
                position=position,
                name=name,
            )
            self.session.add(model)

        await self.session.commit()

    async def get_cached_position(self, user_id: int, tag: str) -> int | None:
        """Возвращает кэшированную позицию категории для тега."""
        model = await self.session.get(TagCategoryCacheModel, (user_id, tag))
        return model.category_position if model else None

    async def cache_position(self, user_id: int, tag: str, position: int) -> None:
        """Кэширует маппинг тег → категория."""
        model = TagCategoryCacheModel(
            user_id=user_id,
            tag=tag,
            category_position=position,
        )
        await self.session.merge(model)
        await self.session.commit()

    async def get_stats(self, user_id: int) -> dict[int, int]:
        """Возвращает статистику: {позиция_категории: количество_записей}."""
        from sqlalchemy import select

        from src.infrastructure.db.models import EntryModel

        # Получаем все записи пользователя с тегами
        stmt = select(EntryModel.id, EntryModel.tags).where(
            EntryModel.user_id == user_id,
            EntryModel.tags.isnot(None),
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return {i: 0 for i in range(5)}

        # Собираем все уникальные теги
        all_tags: set[str] = set()
        for _, tags in rows:
            if tags:
                all_tags.update(tags)

        if not all_tags:
            return {i: 0 for i in range(5)}

        # Получаем маппинг тегов на категории
        cache_stmt = select(TagCategoryCacheModel).where(
            TagCategoryCacheModel.user_id == user_id,
            TagCategoryCacheModel.tag.in_(list(all_tags)),
        )
        cache_result = await self.session.execute(cache_stmt)
        tag_to_position: dict[str, int] = {
            m.tag: m.category_position for m in cache_result.scalars().all()
        }

        # Считаем количество записей для каждой категории
        stats: dict[int, int] = {i: 0 for i in range(5)}
        for _, tags in rows:
            if not tags:
                continue
            # Определяем категорию записи по первому тегу
            first_tag = tags[0]
            position = tag_to_position.get(first_tag, 0)
            stats[position] += 1

        return stats
