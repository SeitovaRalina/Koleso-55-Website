from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, Index, func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserProfile(Base):
    """User profile for recommendation system"""
    
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_vector: Mapped[Optional[list[float]]] = mapped_column(Vector(768), nullable=True)
    ials_factors: Mapped[Optional[list[float]]] = mapped_column(Vector(128), nullable=True)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_user_id", "user_id"),
    )
