from .base import Base

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, DateTime, Integer, Float, String, Text, 
    ForeignKey, Index, BIGINT, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from enums import enums

class Users(Base):
    """Модель пользователя."""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, nullable=False, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")