"""Use case: управление категориями пользователя."""

from __future__ import annotations

from src.domain.entities import UserCategories
from src.domain.exceptions import ValidationError
from src.domain.interfaces import CategoryRepository
from src.application import log_use_case


class ManageCategoriesUseCase:
    """Сценарий: просмотр и изменение категорий для ромба."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def get(self, user_id: int) -> UserCategories:
        """Возвращает категории пользователя."""
        log_use_case.info(f"📂 Получаю категории | user_id={user_id}")
        categories = await self.repository.get_categories(user_id)
        log_use_case.info(f"✅ Категории получены | user_id={user_id}")
        return categories

    async def handle_command(self, user_id: int, raw_args: str) -> UserCategories:
        """Обрабатывает команду /categories с сырыми аргументами.

        Args:
            user_id: ID пользователя.
            raw_args: Сырая строка аргументов (например "set Python AI ..." или "reset").

        Returns:
            Обновлённые категории.

        Raises:
            ValidationError: Если аргументы некорректны.
        """
        parts = raw_args.strip().split(maxsplit=1)
        subcommand = parts[0].lower()

        if subcommand == "reset":
            return await self.reset(user_id)

        if subcommand == "set":
            if len(parts) < 2:
                raise ValidationError(
                    "Укажи 5 категорий через пробел.\n"
                    "Пример: /categories set Python AI Здоровье Бизнес Креатив"
                )
            names = parts[1].split()
            return await self.set(user_id, names)

        raise ValidationError(
            "Неизвестная команда.\n"
            "Использование:\n"
            "/categories — показать\n"
            "/categories set Кат1 Кат2 Кат3 Кат4 Кат5 — установить\n"
            "/categories reset — сбросить"
        )

    async def set(self, user_id: int, names: list[str]) -> UserCategories:
        """Устанавливает пользовательские категории."""
        log_use_case.info(f"⚙️  Устанавливаю категории | user_id={user_id}, категорий={len(names)}")
        
        if len(names) != 5:
            log_use_case.warning(f"⚠️ Неверное количество категорий | user_id={user_id}, получено={len(names)}")
            raise ValidationError(f"Нужно указать ровно 5 категорий, получено {len(names)}")

        # Очищаем и нормализуем названия
        cleaned = [name.strip()[:50] for name in names]
        categories = UserCategories(user_id=user_id, names=cleaned)
        await self.repository.set_categories(categories)
        
        log_use_case.info(f"✅ Категории установлены | user_id={user_id}")
        return categories

    async def reset(self, user_id: int) -> UserCategories:
        """Сбрасывает на категории по умолчанию."""
        log_use_case.info(f"🔄 Сброс категорий на стандартные | user_id={user_id}")
        categories = UserCategories.defaults(user_id)
        await self.repository.set_categories(categories)
        log_use_case.info(f"✅ Категории сброшены | user_id={user_id}")
        return categories
