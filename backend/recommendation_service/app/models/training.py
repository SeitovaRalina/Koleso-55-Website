from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrainingState(Base):
    """Training state tracking for recommendation models"""
    
    __tablename__ = "training_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_training_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_interactions: Mapped[int] = mapped_column(Integer, default=0)
    interactions_since_training: Mapped[int] = mapped_column(Integer, default=0)
    retrain_threshold: Mapped[int] = mapped_column(Integer, default=100)
    models_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __table_args__ = (
        Index("idx_models_ready", "models_ready"),
    )
