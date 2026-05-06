from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.excursion import Excursion

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
def generate_embeddings_for_excursions(self, excursion_ids: list = None):
    """Generate text embeddings for excursions"""
    import asyncio
    
    async def _generate_embeddings():
        try:
            # Load model
            model_name = "DeepPavlov/rubert-base-cased"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Get excursions that need embeddings
            query = select(Excursion).where(Excursion.has_embedding == False)
            if excursion_ids:
                query = query.where(Excursion.excursion_id.in_(excursion_ids))
            
            result = await self.db.execute(query.limit(100))  # Process in batches
            excursions = result.scalars().all()
            
            if not excursions:
                return {"status": "no_excursions_to_process"}
            
            logger.info(f"Generating embeddings for {len(excursions)} excursions")
            
            # Process each excursion
            for excursion in excursions:
                try:
                    # Generate embedding
                    text = excursion.text_for_embedding
                    inputs = tokenizer(
                        text,
                        return_tensors="pt",
                        truncation=True,
                        padding=True,
                        max_length=512
                    )
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        # Use CLS token embedding or mean pooling
                        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                        embedding = embedding.numpy()
                    
                    # Update excursion
                    excursion.embedding = embedding.tolist()
                    excursion.has_embedding = True
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for excursion {excursion.excursion_id}: {e}")
                    continue
            
            await self.db.commit()
            
            return {
                "status": "completed",
                "processed_count": len(excursions)
            }
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            await self.db.rollback()
            raise
    
    return asyncio.run(_generate_embeddings())


@celery_app.task
def cleanup_old_embeddings():
    """Clean up old or unused embeddings (maintenance task)"""
    import asyncio
    
    async def _cleanup():
        try:
            # This is a placeholder for any cleanup logic needed
            # For now, just log that cleanup was run
            logger.info("Embedding cleanup task completed")
            return {"status": "completed"}
            
        except Exception as e:
            logger.error(f"Embedding cleanup failed: {e}")
            raise
    
    return asyncio.run(_cleanup())
