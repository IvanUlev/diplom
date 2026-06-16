"""
Базовый класс для всех моделей.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, DateTime, Integer, Float, String, Text, 
    ForeignKey, Index, BIGINT, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import enum


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
