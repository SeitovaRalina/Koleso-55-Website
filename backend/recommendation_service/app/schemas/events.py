from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


InteractionEventType = Literal["view", "long_view", "favorite", "review", "booking"]
SystemEventType = Literal["content_update", "popularity_update"]


class RecommendationEvent(BaseModel):
    event_type: InteractionEventType | SystemEventType
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    excursion_id: int = Field(..., gt=0)
    weight: Optional[float] = Field(None, ge=0, le=1)
    timestamp: datetime
    source: Optional[str] = None
    duration_seconds: Optional[int] = None

    @model_validator(mode="after")
    def require_actor_for_interactions(self):
        if self.event_type in {"view", "long_view", "favorite", "review", "booking"}:
            if self.user_id is None and not self.session_id:
                raise ValueError("user_id or session_id is required for interaction events")
        return self
