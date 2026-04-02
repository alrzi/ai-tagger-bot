"""Use case: управление категориями пользователя."""

from __future__ import annotations

from src.domain.entities import UserCategories
from src.domain.exceptions import ValidationError
from src.domain.interfaces import CategoryRepository


class ManageCategoriesUseCase:
    """Сценарий: просмотр и изменение категорий для ромба."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def get(self, user_id: int) -> UserCategories:
        """Возвращает категории пользователя."""
        return await self.repository.get_categories(user_id)

    async def set(self, user_id: int, names: list[str]) -> UserCategories:
        """Устанавливает пользовательские категории."""
        if len(names) != 5:
            raise ValidationError(f"Нужно указать ровно 5 категорий, получено {len(names)}")

        # Очищаем и нормализуем названия
        cleaned = [name.strip()[:50] for name in names]
        categories = UserCategories(user_id=user_id, names=cleaned)
        await self.repository.set_categories(categories)
        return categories

    async def reset(self, user_id: int) -> UserCategories:
        """Сбрасывает на категории по умолчанию."""
        categories = UserCategories.defaults(user_id)
        await self.repository.set_categories(categories)
        return categories
