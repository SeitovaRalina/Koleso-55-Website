from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.tasks.training import train_models, sync_excursions_from_django
from app.models.training import TrainingState
from app.schemas.admin import (
    TrainingStatusResponse,
    RetrainResponse,
    SyncResponse
)

router = APIRouter()


@router.post("/retrain", response_model=RetrainResponse)
async def trigger_retraining(
    background_tasks: BackgroundTasks,
    force: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Trigger model retraining"""
    
    try:
        # Check if training is needed
        result = await db.execute(select(TrainingState).limit(1))
        training_state = result.scalar_one_or_none()
        
        if not training_state:
            training_state = TrainingState()
            db.add(training_state)
        
        if not force and training_state.interactions_since_training < training_state.retrain_threshold:
            return RetrainResponse(
                status="skipped",
                reason="Not enough interactions for retraining",
                interactions_since_training=training_state.interactions_since_training,
                threshold=training_state.retrain_threshold
            )
        
        # Add training task to background
        background_tasks.add_task(train_models)
        
        return RetrainResponse(
            status="started",
            message="Model retraining started in background"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-excursions", response_model=SyncResponse)
async def sync_excursions(background_tasks: BackgroundTasks):
    """Sync excursions from Django main service"""
    
    try:
        background_tasks.add_task(sync_excursions_from_django)
        
        return SyncResponse(
            status="started",
            message="Excursion sync started in background"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-status", response_model=TrainingStatusResponse)
async def get_training_status(db: AsyncSession = Depends(get_db)):
    """Get current training status"""
    
    try:
        result = await db.execute(select(TrainingState).limit(1))
        training_state = result.scalar_one_or_none()
        
        if not training_state:
            return TrainingStatusResponse(
                models_ready=False,
                last_training_time=None,
                total_interactions=0,
                interactions_since_training=0,
                retrain_threshold=100
            )
        
        return TrainingStatusResponse(
            models_ready=training_state.models_ready,
            last_training_time=training_state.last_training_time,
            total_interactions=training_state.total_interactions,
            interactions_since_training=training_state.interactions_since_training,
            retrain_threshold=training_state.retrain_threshold
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
