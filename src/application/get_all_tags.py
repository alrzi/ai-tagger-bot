"""Получение всех тегов пользователя."""

from __future__ import annotations

from src.domain.interfaces import TagRepository


class GetAllTagsUseCase:
    """Получить все теги пользователя."""

    def __init__(self, tag_repository: TagRepository) -> None:
        self.tag_repository = tag_repository

    async def execute(self, user_id: int) -> list[str]:
        """Выполнить use case."""
        return await self.tag_repository.get_all_user_tags(user_id)
