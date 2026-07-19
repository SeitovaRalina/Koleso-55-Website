from typing import Dict, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.core.di import get_db
from app.models.training import TrainingState
from app.models.excursions import Excursion
from app.models.profile import UserProfile
from app.models.interaction import UserInteraction
from app.tasks.training import train_ials_model, rebuild_all_caches
from celery.result import AsyncResult


router = APIRouter()


@router.post("/retrain", status_code=202)
async def retrain_models(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger iALS model retraining task
    """
    try:
        # Trigger Celery task and get task ID
        task = train_ials_model.delay()
        
        return {
            "task_id": task.id,
            "message": "iALS model retraining task started",
            "status": "PENDING"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting retraining: {str(e)}"
        )


@router.get("/retrain/{task_id}")
async def get_retrain_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of retraining task
    """
    try:
        result = AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "error": str(result.info) if result.failed() else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting task status: {str(e)}"
        )


@router.post("/rebuild-cache", status_code=202)
async def rebuild_caches(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger cache rebuilding task
    """
    try:
        # Trigger Celery task and get task ID
        task = rebuild_all_caches.delay()
        
        return {
            "task_id": task.id,
            "message": "Cache rebuilding task started",
            "status": "PENDING"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting cache rebuild: {str(e)}"
        )


@router.get("/stats")
async def get_training_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive system statistics
    """
    try:
        # Get training state
        result = await db.execute(
            select(TrainingState).limit(1)
        )
        training_state = result.scalar_one_or_none()
        
        # Get excursion counts
        excursion_result = await db.execute(
            select(
                func.count(Excursion.id).label('total_excursions'),
                func.count(Excursion.id).filter(Excursion.has_embedding == True).label('excursions_with_embeddings'),
                func.count(Excursion.id).filter(Excursion.ials_factors.is_not(None)).label('excursions_with_ials_factors')
            )
        )
        excursion_stats = excursion_result.first()
        
        # Get user counts
        user_result = await db.execute(
            select(
                func.count(UserProfile.user_id).label('total_users'),
                func.count(UserProfile.user_id).filter(UserProfile.content_vector.is_not(None)).label('users_with_content_vectors'),
                func.count(UserProfile.user_id).filter(UserProfile.ials_factors.is_not(None)).label('users_with_ials_factors')
            )
        )
        user_stats = user_result.first()
        
        # Get interaction counts
        interaction_result = await db.execute(
            select(
                func.count(UserInteraction.id).label('total_interactions'),
                func.count(func.distinct(UserInteraction.user_id)).label('active_users'),
                func.count(func.distinct(UserInteraction.excursion_id)).label('interacted_excursions')
            )
        )
        interaction_stats = interaction_result.first()
        
        # Get recent activity
        recent_result = await db.execute(
            select(func.count(UserInteraction.id))
                .where(UserInteraction.timestamp >= datetime.utcnow() - timedelta(hours=24))
        )
        recent_interactions = recent_result.scalar()
        
        stats = {
            "training_state": {
                "total_interactions": training_state.total_interactions if training_state else 0,
                "interactions_since_training": training_state.interactions_since_training if training_state else 0,
                "models_ready": training_state.models_ready if training_state else False,
                "last_training_time": training_state.last_training_time.isoformat() if training_state and training_state.last_training_time else None,
                "retrain_threshold": training_state.retrain_threshold if training_state else 100
            },
            "excursions": {
                "total": excursion_stats.total_excursions or 0,
                "with_embeddings": excursion_stats.excursions_with_embeddings or 0,
                "with_ials_factors": excursion_stats.excursions_with_ials_factors or 0
            },
            "users": {
                "total": user_stats.total_users or 0,
                "with_content_vectors": user_stats.users_with_content_vectors or 0,
                "with_ials_factors": user_stats.users_with_ials_factors or 0
            },
            "interactions": {
                "total": interaction_stats.total_interactions or 0,
                "active_users": interaction_stats.active_users or 0,
                "interacted_excursions": interaction_stats.interacted_excursions or 0,
                "last_24h": recent_interactions or 0
            },
            "system_health": {
                "timestamp": datetime.utcnow().isoformat(),
                "ready_for_training": (training_state.models_ready if training_state else False) and 
                                  (excursion_stats.excursions_with_embeddings or 0) > 0 and
                                  (interaction_stats.total_interactions or 0) >= 100
            }
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting training stats: {str(e)}"
        )
