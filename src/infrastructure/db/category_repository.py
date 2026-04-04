"""Реализация CategoryRepository через SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import UserCategories
from src.infrastructure.db.models import UserCategoryModel


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


    async def get_stats(self, user_id: int) -> dict[int, int]:
        """Возвращает статистику: {позиция_категории: количество_записей}."""
        from sqlalchemy import func, select

        from src.infrastructure.db.models import EntryModel

        # Получаем количество записей по категориям
        stmt = select(
            EntryModel.category_position,
            func.count(EntryModel.id),
        ).where(
            EntryModel.user_id == user_id,
        ).group_by(
            EntryModel.category_position,
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        stats: dict[int, int] = {i: 0 for i in range(5)}
        for position, count in rows:
            stats[position] = count

        return stats
