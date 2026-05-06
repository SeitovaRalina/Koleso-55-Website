from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # NULL for guest users
    session_id = Column(String(100), nullable=True, index=True)
    excursion_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(20), nullable=False)  # view, long_view, favorite, review, booking
    weight = Column(Float, nullable=False)  # 0.3, 0.7, 0.8, 0.9, 1.0
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_interaction_user_excursion', 'user_id', 'excursion_id'),
        Index('idx_user_interaction_session_excursion', 'session_id', 'excursion_id'),
        Index('idx_user_interaction_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<UserInteraction(user_id={self.user_id}, excursion_id={self.excursion_id}, event_type='{self.event_type}')>"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, primary_key=True, index=True)
    content_vector = Column(Vector(768), nullable=True)  # Content-based preferences
    ials_factors = Column(Vector(128), nullable=True)   # Collaborative filtering factors
    interaction_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, interaction_count={self.interaction_count})>"
