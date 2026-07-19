from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request model for recommendations endpoint"""
    user_id: Optional[int] = Field(None, description="User ID for personalized recommendations")
    session_id: Optional[str] = Field(None, description="Session ID for anonymous users")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of recommendations")


class ExcursionRecommendation(BaseModel):
    """Single excursion recommendation"""
    excursion_id: int = Field(..., description="Excursion ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score")
    title: str = Field(..., description="Excursion title")
    category: str = Field(..., description="Excursion category")
    price: float = Field(..., description="Excursion price")


class RecommendationResponse(BaseModel):
    """Response model for recommendations endpoint"""
    recommendations: List[ExcursionRecommendation] = Field(..., description="List of recommended excursions")
    user_id: Optional[int] = Field(None, description="User ID (if provided)")
    session_id: Optional[str] = Field(None, description="Session ID (if provided)")
    algorithm_used: str = Field("hybrid", description="Algorithm used for recommendations")
