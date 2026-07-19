from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RecommendationCache(Base):
    """Persistent snapshot of user recommendation cache."""

    __tablename__ = "recommendation_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    excursion_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    scores: Mapped[list[float]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", name="uq_recommendation_cache_user_id"),)


class SimilarCache(Base):
    """Persistent snapshot of similar excursion cache."""

    __tablename__ = "similar_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    excursion_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    similar_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    scores: Mapped[list[float]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("excursion_id", name="uq_similar_cache_excursion_id"),)
