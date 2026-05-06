from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class TrainingState(Base):
    __tablename__ = "training_state"
    
    id = Column(Integer, primary_key=True, index=True)
    last_training_time = Column(DateTime(timezone=True), nullable=True)
    total_interactions = Column(Integer, default=0)
    interactions_since_training = Column(Integer, default=0)
    retrain_threshold = Column(Integer, default=100)
    models_ready = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<TrainingState(models_ready={self.models_ready}, interactions_since_training={self.interactions_since_training})>"
