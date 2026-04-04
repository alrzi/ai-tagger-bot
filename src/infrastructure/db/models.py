"""SQLAlchemy ORM модели."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, DateTime, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EntryModel(Base):
    """ORM модель записи пользователя."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    category_position: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, default="")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<EntryModel(id={self.id}, user_id={self.user_id}, title='{self.title[:30]}')>"


class UserCategoryModel(Base):
    """ORM модель категории пользователя."""

    __tablename__ = "user_categories"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    position: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"<UserCategoryModel(user_id={self.user_id}, position={self.position}, name='{self.name}')>"


class TagModel(Base):
    """ORM модель тега."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "normalized_name"),
    )

    def __repr__(self) -> str:
        return f"<TagModel(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class EntryTagModel(Base):
    """Связующая таблица запись ↔ тег."""

    __tablename__ = "entry_tags"

    entry_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def __repr__(self) -> str:
        return f"<EntryTagModel(entry_id={self.entry_id}, tag_id={self.tag_id})>"


class ChunkModel(Base):
    """ORM модель чанка текста для детального поиска."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(Vector(768), nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<ChunkModel(id={self.id}, entry_id={self.entry_id}, position={self.position})>"
