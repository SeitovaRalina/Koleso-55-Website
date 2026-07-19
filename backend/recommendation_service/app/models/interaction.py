from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Float, Boolean, DateTime, Text, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserInteraction(Base):
    """User interaction events for recommendation system"""
    
    __tablename__ = "user_interactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    excursion_id: Mapped[int] = mapped_column(Integer, index=True)
    event_type: Mapped[str] = mapped_column(String(50))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_session_id", "session_id"),
        Index("idx_excursion_id", "excursion_id"),
        Index("idx_timestamp", "timestamp"),
    )
