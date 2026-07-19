from typing import List
from pydantic import BaseModel, Field


class SimilarRequest(BaseModel):
    """Request model for similar excursions endpoint"""
    excursion_id: int = Field(..., description="Excursion ID to find similar items for")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of similar excursions")


class SimilarExcursion(BaseModel):
    """Similar excursion model"""
    excursion_id: int = Field(..., description="Excursion ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    title: str = Field(..., description="Excursion title")
    category: str = Field(..., description="Excursion category")
    price: float = Field(..., description="Excursion price")


class SimilarResponse(BaseModel):
    """Response model for similar excursions endpoint"""
    similar_excursions: List[SimilarExcursion] = Field(..., description="List of similar excursions")
    excursion_id: int = Field(..., description="Original excursion ID")
    algorithm_used: str = Field("content_based", description="Algorithm used for similarity")
