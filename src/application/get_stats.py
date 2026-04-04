"""Use case: получение статистики по категориям."""

from __future__ import annotations

from src.domain.entities import UserCategories
from src.domain.interfaces import CategoryRepository
from src.application import log_use_case


class GetStatsUseCase:
    """Сценарий: получить статистику записей по категориям."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int) -> tuple[UserCategories, dict[int, int]]:
        """Возвращает категории и статистику.

        Returns:
            Кортеж (категории, {позиция: количество_записей}).
        """
        log_use_case.info(f"📊 Начинаю GetStats | user_id={user_id}")
        categories = await self.repository.get_categories(user_id)
        stats = await self.repository.get_stats(user_id)
        log_use_case.info(f"✅ Статистика получена | категорий={len(categories.names)}, записей={sum(stats.values())}")
        return categories, stats
