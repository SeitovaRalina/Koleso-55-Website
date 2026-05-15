from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Base class for all models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    __abstract__ = True
