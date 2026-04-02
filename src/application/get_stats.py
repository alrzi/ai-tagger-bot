"""Use case: получение статистики по категориям."""

from __future__ import annotations

from src.domain.entities import UserCategories
from src.domain.interfaces import CategoryRepository


class GetStatsUseCase:
    """Сценарий: получить статистику записей по категориям."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int) -> tuple[UserCategories, dict[int, int]]:
        """Возвращает категории и статистику.

        Returns:
            Кортеж (категории, {позиция: количество_записей}).
        """
        categories = await self.repository.get_categories(user_id)
        stats = await self.repository.get_stats(user_id)
        return categories, stats
