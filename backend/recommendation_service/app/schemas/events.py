from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class EventData(BaseModel):
    """Event data from RabbitMQ"""
    event_type: str = Field(..., description="Type of event: view, long_view, favorite, review, booking")
    user_id: Optional[int] = Field(None, description="User ID (null for guests)")
    session_id: Optional[str] = Field(None, max_length=100, description="Session ID for guests")
    item_id: int = Field(..., description="Excursion ID")
    weight: float = Field(..., ge=0.0, le=1.0, description="Event weight")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds for view events")
    source: Optional[str] = Field(None, description="Source of interaction: search, category, etc.")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['view', 'long_view', 'favorite', 'review', 'booking', 'content_update', 'popularity_update']
        if v not in allowed_types:
            raise ValueError(f'event_type must be one of: {allowed_types}')
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('timestamp must be valid ISO 8601 format')
        return v


class EventResponse(BaseModel):
    """Event processing response"""
    success: bool = Field(..., description="Whether event was processed successfully")
    message: Optional[str] = Field(None, description="Processing message")


class PopularityUpdate(BaseModel):
    """Popularity update data"""
    excursion_id: int = Field(..., description="Excursion ID")
    bookings_count: int = Field(..., ge=0, description="Number of bookings")


class ContentUpdate(BaseModel):
    """Content update data"""
    excursion_id: int = Field(..., description="Excursion ID")
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    category: Optional[str] = Field(None, description="Updated category")
