"""Реализация CategoryRepository через SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import Row, delete, select
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
