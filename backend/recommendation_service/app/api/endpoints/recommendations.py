from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.user import UserProfile
from app.models.excursion import Excursion
from app.models.user import UserInteraction
from app.models.cache import RecommendationCache, SimilarCache
from app.services.recommendation_engine import get_user_recommendations, get_similar_excursions
from app.services.cache import get_cached_recommendations, set_cached_recommendations
from app.schemas.recommendations import (
    UserRecommendationsResponse,
    RecommendationItem,
    RecommendationBreakdown,
    SimilarItemsResponse,
    SimilarItem,
    SimilarItemBreakdown,
    PopularItemsResponse,
    PopularItem
)

router = APIRouter()


@router.get("/user/{user_id}", response_model=UserRecommendationsResponse)
async def get_recommendations_for_user(
    user_id: int,
    top_k: int = Query(default=20, ge=1, le=100),
    exclude_interacted: bool = Query(default=True),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized recommendations for a user"""
    
    try:
        # Check cache first (workflow requirement: "rec:user:{user_id}")
        cached_result = await get_cached_recommendations(f"rec:user:{user_id}")
        if cached_result:
            # Convert cached data to Pydantic models
            recommendation_items = [
                RecommendationItem(
                    excursion_id=rec["excursion_id"],
                    score=rec["score"],
                    breakdown=RecommendationBreakdown(**rec["breakdown"]) if rec.get("breakdown") else None
                )
                for rec in cached_result
            ]
            return UserRecommendationsResponse(user_id=user_id, recommendations=recommendation_items)
        
        # Get recommendations
        recommendations = await get_user_recommendations(
            db, user_id, top_k, exclude_interacted
        )
        
        # Convert to Pydantic models
        recommendation_items = [
            RecommendationItem(
                excursion_id=rec["excursion_id"],
                score=rec["score"],
                breakdown=RecommendationBreakdown(**rec["breakdown"]) if rec.get("breakdown") else None
            )
            for rec in recommendations
        ]
        
        # Cache result (workflow requirement: TTL=3600 and cache key "rec:user:{user_id}")
        await set_cached_recommendations(f"rec:user:{user_id}", recommendations, ttl=3600)
        
        return UserRecommendationsResponse(user_id=user_id, recommendations=recommendation_items)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{excursion_id}", response_model=SimilarItemsResponse)
async def get_similar_items(
    excursion_id: int,
    top_k: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get similar excursions for a given excursion"""
    
    try:
        # Check cache first (workflow requirement: "sim:{excursion_id}")
        cached_result = await get_cached_recommendations(f"sim:{excursion_id}")
        if cached_result:
            # Convert cached data to Pydantic models
            similar_items = [
                SimilarItem(
                    excursion_id=item["excursion_id"],
                    score=item["score"],
                    breakdown=SimilarItemBreakdown(**item["breakdown"]) if item.get("breakdown") else None
                )
                for item in cached_result
            ]
            return SimilarItemsResponse(excursion_id=excursion_id, similar_items=similar_items)
        
        # Get similar items
        similar_items_data = await get_similar_excursions(db, excursion_id, top_k)
        
        # Convert to Pydantic models
        similar_items = [
            SimilarItem(
                excursion_id=item["excursion_id"],
                score=item["score"],
                breakdown=SimilarItemBreakdown(**item["breakdown"]) if item.get("breakdown") else None
            )
            for item in similar_items_data
        ]
        
        # Cache result (workflow requirement: cache key "sim:{excursion_id}")
        await set_cached_recommendations(f"sim:{excursion_id}", similar_items_data, ttl=7200)
        
        return SimilarItemsResponse(excursion_id=excursion_id, similar_items=similar_items)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular", response_model=PopularItemsResponse)
async def get_popular_excursions(
    top_k: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get popular excursions for cold start"""
    
    try:
        query = select(Excursion).where(Excursion.has_embedding == True)
        
        if category:
            query = query.where(Excursion.category == category)
        
        query = query.order_by(Excursion.popularity.desc()).limit(top_k)
        
        result = await db.execute(query)
        excursions = result.scalars().all()
        
        popular_items = [
            PopularItem(
                excursion_id=exc.excursion_id,
                title=exc.title,
                category=exc.category,
                popularity=exc.popularity,
                average_rating=exc.average_rating,
                score=1.0  # Popular items get score of 1.0
            )
            for exc in excursions
        ]
        
        return PopularItemsResponse(popular_items=popular_items)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
