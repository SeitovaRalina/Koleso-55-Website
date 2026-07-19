from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.di import get_db, get_content_service
from app.schemas.similar import SimilarResponse, SimilarRequest


router = APIRouter()


@router.get("/{excursion_id}", response_model=SimilarResponse)
async def get_similar_excursions(
    excursion_id: int = Path(..., description="Excursion ID to find similar items for"),
    top_k: int = Query(10, ge=1, le=50, description="Maximum number of similar excursions"),
    db: AsyncSession = Depends(get_db),
    content_service = Depends(get_content_service)
):
    """
    Get similar excursions based on content
    """
    try:
        similar_excursions = await content_service.get_similar_excursions(
            excursion_id=excursion_id,
            limit=top_k
        )
        
        return SimilarResponse(
            similar_excursions=similar_excursions,
            excursion_id=excursion_id,
            algorithm_used="content_based"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding similar excursions: {str(e)}"
        )
