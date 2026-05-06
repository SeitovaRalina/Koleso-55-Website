from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Index
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Excursion(Base):
    __tablename__ = "excursions"

    id = Column(Integer, primary_key=True, index=True)
    excursion_id = Column(Integer, unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    location_type = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    average_rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    popularity = Column(Integer, default=0)  # bookings count
    text_for_embedding = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=True)
    ials_factors = Column(Vector(128), nullable=True)
    has_embedding = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for performance
    __table_args__ = (
        Index('idx_excursion_category', 'category'),
        Index('idx_excursion_popularity', 'popularity'),
        Index('idx_excursion_has_embedding', 'has_embedding'),
        # Vector indexes will be created separately in migrations
    )

    def __repr__(self):
        return f"<Excursion(id={self.excursion_id}, title='{self.title}')>"
