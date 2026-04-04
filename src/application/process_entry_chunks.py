"""Сценарий: обработка чанков записи для RAG."""

from __future__ import annotations

import asyncio
from asyncio import Semaphore

from src.domain.interfaces import (
    ChunkRepository,
    EmbeddingGenerator,
)
from src.domain.text_chunker import TextChunker
from src.application import log_use_case, log_ai


class ProcessEntryChunksInteractor:
    """Генерирует и сохраняет чанки текста записи с эмбеддингами."""

    MAX_CONCURRENT_EMBEDDINGS = 4

    def __init__(
        self,
        chunk_repository: ChunkRepository,
        embedder: EmbeddingGenerator,
        text_chunker: TextChunker,
    ) -> None:
        self.chunk_repository = chunk_repository
        self.embedder = embedder
        self.text_chunker = text_chunker
        self.semaphore = Semaphore(self.MAX_CONCURRENT_EMBEDDINGS)

    async def execute(self, entry_id: int, raw_text: str) -> int:
        """Обработать чанки для записи. Возвращает количество созданных чанков."""
        log_use_case.info(f"📄 Начинаю ProcessEntryChunks | entry_id={entry_id}")

        # Шаг 1: Удаляем старые чанки
        await self.chunk_repository.delete_by_entry_id(entry_id)
        log_use_case.info(f"🗑️  Старые чанки удалены | entry_id={entry_id}")

        # Шаг 2: Разбиваем текст на чанки
        chunks = self.text_chunker.split(raw_text)

        if not chunks:
            log_use_case.warning(f"⚠️ Нет чанков для записи | entry_id={entry_id}")
            return 0

        log_ai.info(f"🧠 Начинаю генерацию эмбеддингов | entry_id={entry_id}, чанков={len(chunks)}")

        # Шаг 3: Параллельная генерация эмбеддингов
        embedding_tasks = [
            self._generate_embedding(chunk_text)
            for chunk_text in chunks
        ]

        results: list[list[float] | BaseException] = await asyncio.gather(*embedding_tasks, return_exceptions=True)

        # Шаг 4: Фильтрация успешных результатов
        successful_chunks: list[tuple[str, list[float]]] = []
        failed_count = 0

        for chunk_text, embedding_result in zip(chunks, results):
            if isinstance(embedding_result, BaseException):
                log_ai.error(f"❌ Ошибка генерации эмбеддинга: {str(embedding_result)}")
                failed_count += 1
                continue

            successful_chunks.append((chunk_text, embedding_result))

        # Шаг 5: Массовое сохранение
        if successful_chunks:
            await self.chunk_repository.save_chunks(entry_id, successful_chunks)

        log_use_case.info(
            f"✅ Обработка чанков завершена | entry_id={entry_id}, успешно={len(successful_chunks)}, ошибок={failed_count}"
        )

        return len(successful_chunks)

    async def _generate_embedding(self, text: str) -> list[float]:
        """Генерирует эмбеддинг с ограничением параллелизма."""
        async with self.semaphore:
            return await self.embedder.embed(text)
