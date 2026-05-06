from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class RecommendationBreakdown(BaseModel):
    """Breakdown of recommendation score components"""
    content: float = Field(..., description="Content-based similarity score")
    collab: float = Field(..., description="Collaborative filtering score")
    popularity: float = Field(..., description="Popularity-based score")


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    excursion_id: int = Field(..., description="Excursion ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Overall recommendation score")
    breakdown: Optional[RecommendationBreakdown] = Field(None, description="Score breakdown")


class UserRecommendationsResponse(BaseModel):
    """Response for user recommendations"""
    user_id: int = Field(..., description="User ID")
    recommendations: List[RecommendationItem] = Field(..., description="List of recommendations")


class SimilarItemBreakdown(BaseModel):
    """Breakdown of similarity score components"""
    content_similarity: float = Field(..., description="Content similarity score")
    category_bonus: float = Field(..., description="Category match bonus")


class SimilarItem(BaseModel):
    """Single similar item"""
    excursion_id: int = Field(..., description="Excursion ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    breakdown: Optional[SimilarItemBreakdown] = Field(None, description="Score breakdown")


class SimilarItemsResponse(BaseModel):
    """Response for similar items"""
    excursion_id: int = Field(..., description="Original excursion ID")
    similar_items: List[SimilarItem] = Field(..., description="List of similar items")


class PopularItem(BaseModel):
    """Popular excursion item"""
    excursion_id: int = Field(..., description="Excursion ID")
    title: str = Field(..., description="Excursion title")
    category: str = Field(..., description="Excursion category")
    popularity: int = Field(..., ge=0, description="Popularity score")
    average_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Average rating")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score")


class PopularItemsResponse(BaseModel):
    """Response for popular items"""
    popular_items: List[PopularItem] = Field(..., description="List of popular items")
