"""Use case: анализ записи через ИИ по новой диаграмме flow."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.interfaces import (
    CategoryRepository,
    EmbeddingGenerator,
    EntryAnalysisService,
    EntryRepository,
    TagRepository,
)
from src.application.sync_entry_tags import SyncEntryTags
from src.application.process_entry_chunks import ProcessEntryChunksInteractor
from src.application import log_use_case, log_ai, log_db


class AnalyzeEntryInteractor:
    """Сценарий: анализ записи через ИИ → summary + category + tags + embedding + chunks."""

    def __init__(
        self,
        entry_repository: EntryRepository,
        tag_repository: TagRepository,
        analysis_service: EntryAnalysisService,
        embedder: EmbeddingGenerator,
        category_repository: CategoryRepository,
        sync_entry_tags: SyncEntryTags,
        process_entry_chunks: ProcessEntryChunksInteractor,
    ) -> None:
        self.entry_repository = entry_repository
        self.tag_repository = tag_repository
        self.analysis_service = analysis_service
        self.embedder = embedder
        self.category_repository = category_repository
        self.sync_entry_tags = sync_entry_tags
        self.process_entry_chunks = process_entry_chunks

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        log_use_case.info(f"🚀 Начинаю AnalyzeEntry | entry_id={entry_id}, user_id={user_id}")

        entry = await self.entry_repository.get_by_id(entry_id, user_id)
        if entry is None:
            log_use_case.warning(f"⚠️ Запись не найдена | entry_id={entry_id}, user_id={user_id}")
            raise NotFoundError(f"Запись {entry_id} не найдена")

        if not entry.raw_text.strip():
            log_use_case.warning(f"⚠️ Пустой текст для анализа | entry_id={entry_id}")
            raise ValidationError("Нет текста для анализа")

        # Шаг 1: Получаем существующие данные пользователя
        log_db.info(f"🔍 Загружаю категории и теги | user_id={user_id}")
        categories = await self.category_repository.get_categories(user_id)
        existing_tags = await self.tag_repository.get_all_user_tags(user_id)

        # Шаг 2: Умная классификация через ИИ
        log_ai.info(f"🤖 Отправляю на анализ в ИИ | entry_id={entry_id}")
        result = await self.analysis_service.analyze(entry.raw_text, categories, existing_tags)
        entry.apply_analysis(result)

        # Шаг 3: Определяем категорию записи
        category_index = categories.names.index(result.category) if result.category in categories.names else 0
        entry.category_position = category_index

        # Шаг 4: Сохраняем главную запись с эмбеддингом
        log_ai.info(f"🧠 Генерирую эмбеддинг | entry_id={entry_id}")
        text_to_embed = entry.get_text_for_embedding()
        entry.embedding = await self.embedder.embed(text_to_embed)
        saved_entry = await self.entry_repository.save(entry)

        # Инициализируем переменную для избежания ошибки unbound
        chunks_count = 0
        if saved_entry.id is not None:
            # Шаг 5: Борьба с дубликатами тегов и нормализация
            log_use_case.info(f"🔖 Синхронизирую теги | entry_id={saved_entry.id}, тегов={len(result.tags)}")
            await self.sync_entry_tags(entry_id=saved_entry.id, user_id=user_id, tags=result.tags)
            
            # Обновляем теги в возвращаемом объекте, так как они сохраняются в отдельной таблице
            saved_entry.tags = result.tags

            # Шаг 6: Рекурсивная грануляция текста для RAG и сохранение чанков
            log_use_case.info(f"📄 Разбиваю на чанки | entry_id={saved_entry.id}")
            chunks_count = await self.process_entry_chunks.execute(saved_entry.id, entry.raw_text)

        log_use_case.info(
            f"✅ Анализ завершен | entry_id={entry_id}, категория={category_index}, тегов={len(result.tags)}, чанков={chunks_count}"
        )

        return saved_entry

