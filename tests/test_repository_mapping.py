"""Тесты для маппинга Row → Entry в PostgresEntryRepository."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.domain.entities import ContentType, Entry
from src.infrastructure.db.repositories import PostgresEntryRepository


@pytest.mark.asyncio
async def test_row_to_entry_mapping() -> None:
    """Маппинг Row → Entry работает корректно."""
    mock_row = MagicMock()
    mock_row._mapping = {
        "id": 1,
        "user_id": 123,
        "url": "https://example.com",
        "title": "Заголовок",
        "raw_text": "Текст записи",
        "summary": "Краткое описание",
        "tags": ["python", "ai"],
        "content_type": "article",
        "embedding": "[0.1, 0.2, 0.3]",
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "similarity": 0.95,
    }

    repo = PostgresEntryRepository(session=None)  # type: ignore[arg-type]
    entry, similarity = repo._row_to_entry(mock_row)

    assert entry.id == 1
    assert entry.user_id == 123
    assert entry.url == "https://example.com"
    assert entry.title == "Заголовок"
    assert entry.raw_text == "Текст записи"
    assert entry.summary == "Краткое описание"
    assert entry.tags == ["python", "ai"]
    assert entry.content_type == ContentType.ARTICLE
    assert entry.embedding == [0.1, 0.2, 0.3]
    assert similarity == 0.95


@pytest.mark.asyncio
async def test_row_to_entry_with_empty_values() -> None:
    """Пустые значения маппятся корректно."""
    mock_row = MagicMock()
    mock_row._mapping = {
        "id": 2,
        "user_id": 456,
        "url": None,
        "title": None,
        "raw_text": None,
        "summary": None,
        "tags": None,
        "content_type": None,
        "embedding": None,
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "similarity": 0.0,
    }

    repo = PostgresEntryRepository(session=None)  # type: ignore[arg-type]
    entry, similarity = repo._row_to_entry(mock_row)

    assert entry.id == 2
    assert entry.user_id == 456
    assert entry.url is None
    assert entry.title == ""
    assert entry.raw_text == ""
    assert entry.summary == ""
    assert entry.tags == []  # Не None!
    assert entry.content_type == ContentType.UNKNOWN
    assert entry.embedding is None
    assert similarity == 0.0


@pytest.mark.asyncio
async def test_row_to_entry_content_type_parsing() -> None:
    """ContentType парсится из строки корректно."""
    test_cases = [
        ("article", ContentType.ARTICLE),
        ("note", ContentType.NOTE),
        ("tutorial", ContentType.TUTORIAL),
        ("unknown", ContentType.UNKNOWN),
    ]

    for content_type_str, expected in test_cases:
        mock_row = MagicMock()
        mock_row._mapping = {
            "id": 1,
            "user_id": 1,
            "url": None,
            "title": None,
            "raw_text": "text",
            "summary": None,
            "tags": None,
            "content_type": content_type_str,
            "embedding": None,
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "similarity": 0.0,
        }

        repo = PostgresEntryRepository(session=None)  # type: ignore[arg-type]
        entry, _ = repo._row_to_entry(mock_row)

        assert entry.content_type == expected, f"Failed for content_type={content_type_str}"


@pytest.mark.asyncio
async def test_row_to_entry_embedding_from_json_string() -> None:
    """Embedding парсится из JSON-строки."""
    mock_row = MagicMock()
    mock_row._mapping = {
        "id": 1,
        "user_id": 1,
        "url": None,
        "title": None,
        "raw_text": "text",
        "summary": None,
        "tags": None,
        "content_type": "article",
        "embedding": "[0.1, 0.2, 0.3, 0.4]",
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "similarity": 0.0,
    }

    repo = PostgresEntryRepository(session=None)  # type: ignore[arg-type]
    entry, _ = repo._row_to_entry(mock_row)

    assert entry.embedding == [0.1, 0.2, 0.3, 0.4]
