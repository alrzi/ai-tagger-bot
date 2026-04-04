"""Доменный сервис для умного разбиения текста на чанки."""

from __future__ import annotations

import re
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Разбивает текст на чанки с сохранением целостности предложений и перекрытием."""

    def __init__(
        self,
        chunk_size: int = 800,
        overlap: int = 80,
        overlap_sentences: int = 2,
    ) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.overlap_sentences = overlap_sentences

        # Регулярное выражение для разделения по предложениям
        self.sentence_splitter = re.compile(r'(?<=[.!?])\s+')

    def split(self, text: str) -> list[str]:
        """Разбивает текст на чанки с учётом естественных границ."""
        if not text.strip():
            return []

        if len(text) <= self.chunk_size:
            return [text]

        sentences = self._split_to_sentences(text)

        if not sentences:
            return [text]

        chunks = self._build_chunks(sentences)

        logger.debug(
            "Текст разбит на %d чанков (длина текста %d)",
            len(chunks),
            len(text),
        )

        return chunks

    def _split_to_sentences(self, text: str) -> list[str]:
        """Разбивает текст на предложения."""
        sentences = self.sentence_splitter.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def _build_chunks(self, sentences: list[str]) -> list[str]:
        """Строит чанки из предложений с перекрытием."""
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length: int = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # Если добавление предложения превысит размер чанка
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Сохраняем готовый чанк
                chunks.append(' '.join(current_chunk))

                # Оставляем перекрытие из последних предложений
                if self.overlap_sentences > 0 and len(current_chunk) > self.overlap_sentences:
                    current_chunk = current_chunk[-self.overlap_sentences:]
                    current_length = sum(len(s) for s in current_chunk) + len(current_chunk) - 1
                else:
                    current_chunk = []
                    current_length = 0

            # Добавляем предложение в текущий чанк
            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 для пробела

        # Добавляем последний чанк
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
