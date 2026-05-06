from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
import logging
from typing import Dict, Any
from datetime import datetime

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.training import TrainingState
from app.models.user import UserInteraction
from app.services.ml_models import train_ials_model, update_content_embeddings
from app.services.django_sync import sync_excursions_from_django

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    
    def __init__(self):
        self._db = None

    @property
    def db(self) -> AsyncSession:
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Clean up database session after task completion"""
        if self._db:
            import asyncio
            asyncio.create_task(self._db.close())
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True)
def train_models(self):
    """Train ML models (IALS and content embeddings)"""
    import asyncio
    
    async def _train_models():
        try:
            # Get training state
            result = await self.db.execute(select(TrainingState).limit(1))
            training_state = result.scalar_one_or_none()
            
            if not training_state:
                training_state = TrainingState()
                self.db.add(training_state)
            
            logger.info("Starting model training...")
            
            # Train IALS collaborative filtering model
            await train_ials_model(self.db)
            
            # Update content embeddings
            await update_content_embeddings(self.db)
            
            # Update training state
            training_state.last_training_time = datetime.utcnow()
            training_state.interactions_since_training = 0
            training_state.models_ready = True
            
            await self.db.commit()
            
            logger.info("Model training completed successfully")
            return {"status": "completed", "models_ready": True}
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            await self.db.rollback()
            raise
    
    return asyncio.run(_train_models())


@celery_app.task(base=DatabaseTask, bind=True)
def check_training_needed(self):
    """Check if training is needed and trigger if so"""
    import asyncio
    
    async def _check_training():
        try:
            result = await self.db.execute(select(TrainingState).limit(1))
            training_state = result.scalar_one_or_none()
            
            if not training_state:
                return {"status": "no_training_state"}
            
            if (training_state.interactions_since_training >= 
                training_state.retrain_threshold):
                
                # Trigger training
                train_models.delay()
                
                return {
                    "status": "training_triggered",
                    "interactions_since_training": training_state.interactions_since_training,
                    "threshold": training_state.retrain_threshold
                }
            
            return {
                "status": "training_not_needed",
                "interactions_since_training": training_state.interactions_since_training,
                "threshold": training_state.retrain_threshold
            }
            
        except Exception as e:
            logger.error(f"Training check failed: {e}")
            raise
    
    return asyncio.run(_check_training())


@celery_app.task
def sync_excursions():
    """Sync excursions from Django main service"""
    import asyncio
    
    async def _sync_excursions():
        try:
            await sync_excursions_from_django()
            logger.info("Excursion sync completed")
            return {"status": "completed"}
            
        except Exception as e:
            logger.error(f"Excursion sync failed: {e}")
            raise
    
    return asyncio.run(_sync_excursions())
