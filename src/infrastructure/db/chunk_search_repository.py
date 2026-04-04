"""Репозиторий семантического поиска по чанкам через pgvector."""

from __future__ import annotations

import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces import VectorSearcher


class PostgresChunkSearchRepository(VectorSearcher):
    """
    Репозиторий для семантического поиска по чанкам.

    ❗️ Требуемые индексы для производительности:
    CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
    CREATE INDEX ON entries (user_id, category_position);
    """

    __SEARCH_QUERY = text("""
        WITH vector_search AS (
            SELECT 
                c.entry_id, 
                c.text AS chunk_text, 
                (c.embedding <=> :vec) AS distance 
            FROM chunks c
            JOIN entries e ON c.entry_id = e.id
            WHERE e.user_id = :uid 
              AND (
                CASE WHEN CAST(:cat_id AS smallint) IS NULL THEN TRUE
                ELSE e.category_position = CAST(:cat_id AS smallint)
                END
              )
            ORDER BY distance ASC
            LIMIT :lim
        )
        SELECT 
            vs.chunk_text,
            vs.distance,
            e.id,
            e.user_id,
            e.category_position,
            e.url,
            e.title,
            e.raw_text,
            e.summary,
            e.is_read,
            e.created_at,
            uc.name AS category_name
        FROM vector_search vs
        JOIN entries e ON vs.entry_id = e.id
        LEFT JOIN user_categories uc 
            ON e.category_position = uc.position 
            AND e.user_id = uc.user_id
    """)

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_with_chunks(
        self, 
        user_id: int, 
        query_vector: list[float], 
        category_id: int | None = None, 
        limit: int = 5
    ) -> list[dict[str, object]]:
        """Выполняет семантический поиск по чанкам."""

        if limit < 1:
            return []

        if not query_vector:
            return []

        result = await self.session.execute(
            self.__SEARCH_QUERY,
            {
                "vec": json.dumps(query_vector),
                "uid": user_id,
                "cat_id": category_id,
                "lim": limit,
            },
        )

        return [
            {
                "entry_id": row.id,
                "chunk_text": row.chunk_text,
                "distance": row.distance,
                "category_name": row.category_name,
                "user_id": row.user_id,
                "category_position": row.category_position,
                "url": row.url,
                "title": row.title or "",
                "raw_text": row.raw_text or "",
                "summary": row.summary or "",
                "is_read": row.is_read,
                "created_at": row.created_at,
            }
            for row in result.all()
        ]
