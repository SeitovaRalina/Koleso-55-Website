from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    excursion_ids = Column(JSON, nullable=False)  # List of ints
    scores = Column(JSON, nullable=False)         # List of floats
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RecommendationCache(user_id={self.user_id}, items_count={len(self.excursion_ids)})>"


class SimilarCache(Base):
    __tablename__ = "similar_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    excursion_id = Column(Integer, unique=True, index=True)
    similar_ids = Column(JSON, nullable=False)    # List of ints
    scores = Column(JSON, nullable=False)          # List of floats
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SimilarCache(excursion_id={self.excursion_id}, similar_count={len(self.similar_ids)})>"
