"""SQLAlchemy ORM модели."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, DateTime, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EntryModel(Base):
    """ORM модель записи пользователя."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, default="")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    content_type: Mapped[str] = mapped_column(String(20), default="unknown")
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(4096), nullable=True)
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


class TagCategoryCacheModel(Base):
    """ORM модель кэша маппинга тег → категория."""

    __tablename__ = "tag_category_cache"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag: Mapped[str] = mapped_column(String(100), primary_key=True)
    category_position: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    def __repr__(self) -> str:
        return f"<TagCategoryCacheModel(user_id={self.user_id}, tag='{self.tag}')>"
