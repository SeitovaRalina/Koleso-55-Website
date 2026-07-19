from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.di import get_db, get_hybrid_service
from app.schemas.recommendations import RecommendationResponse, RecommendationRequest

from app.services.hybrid import HybridService

router = APIRouter()


@router.get("/user/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(
    user_id: int = Path(..., description="User ID for personalized recommendations"),
    top_k: int = Query(20, ge=1, le=100, description="Maximum number of recommendations"),
    exclude_interacted: bool = Query(True, description="Exclude previously interacted items"),
    db: AsyncSession = Depends(get_db),
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """
    Get personalized recommendations for a user
    """
    try:
        recommendations = await hybrid_service.get_user_recommendations(
            user_id=user_id,
            limit=top_k,
            exclude_interacted=exclude_interacted
        )

        return RecommendationResponse(
            recommendations=recommendations,
            user_id=user_id,
            session_id=None,
            algorithm_used="hybrid"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: Optional[int] = Query(None, description="User ID for personalized recommendations"),
    session_id: Optional[str] = Query(None, description="Session ID for anonymous users"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of recommendations"),
    db: AsyncSession = Depends(get_db),
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """
    Get personalized recommendations for a user or session
    """
    try:
        if not user_id and not session_id:
            raise HTTPException(
                status_code=400,
                detail="Either user_id or session_id must be provided"
            )

        recommendations = await hybrid_service.get_user_recommendations(
            user_id=user_id,
            session_id=session_id,
            limit=limit,
            exclude_interacted=True
        )

        return RecommendationResponse(
            recommendations=recommendations,
            user_id=user_id,
            session_id=session_id,
            algorithm_used="hybrid"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )
