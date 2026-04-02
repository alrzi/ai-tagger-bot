"""Доменные исключения приложения."""


class AppError(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    """Ошибка валидации входных данных."""


class NotFoundError(AppError):
    """Сущность не найдена."""


class ParseError(AppError):
    """Ошибка парсинга внешних данных."""
