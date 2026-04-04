"""Нормализация тегов."""

from __future__ import annotations

import re


class TagNormalizer:
    """Нормализует имя тега для обеспечения уникальности.
    
    Отвечает только за преобразование строки, не имеет никаких зависимостей,
    полностью тестируемый чистый объект.
    """

    _INVALID_CHARS_PATTERN = re.compile(r'[^\w\s-]', re.UNICODE)
    _WHITESPACE_PATTERN = re.compile(r'[\s_-]+')

    @classmethod
    def normalize(cls, tag: str) -> str:
        """Нормализовать имя тега."""
        tag = tag.lower().strip()
        tag = cls._INVALID_CHARS_PATTERN.sub('', tag)
        tag = cls._WHITESPACE_PATTERN.sub('_', tag)
        return tag.strip('_')

    @classmethod
    def normalize_list(cls, tags: list[str]) -> dict[str, str]:
        """Нормализовать список тегов, удалить дубликаты и пустые значения.
        
        Возвращает словарь {normalized_name: original_name}
        """
        return {
            cls.normalize(tag): tag.strip()
            for tag in tags
            if tag.strip()
        }
