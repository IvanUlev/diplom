from .base import Base

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, DateTime, Integer, Float, String, Text, 
    ForeignKey, Index, BIGINT, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from enums import enums

class Settings(Base):
    """Настройки системы."""
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
