import logging
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.models.excursion import Excursion
from app.models.user import UserInteraction, UserProfile
from app.models.training import TrainingState

logger = logging.getLogger(__name__)


async def train_ials_model(db: AsyncSession) -> bool:
    """Train IALS collaborative filtering model"""
    
    try:
        logger.info("Starting IALS model training...")
        
        # Get user-item interaction matrix
        result = await db.execute(
            select(UserInteraction.user_id, UserInteraction.excursion_id, UserInteraction.weight)
            .where(UserInteraction.user_id.isnot(None))
        )
        interactions = result.all()
        
        if not interactions:
            logger.warning("No user interactions found for training")
            return False
        
        # Create user-item matrix
        user_ids = list(set(inter.user_id for inter in interactions))
        excursion_ids = list(set(inter.excursion_id for inter in interactions))
        
        user_id_map = {uid: i for i, uid in enumerate(user_ids)}
        excursion_id_map = {eid: i for i, eid in enumerate(excursion_ids)}
        
        # Create sparse matrix
        from scipy.sparse import csr_matrix
        
        rows = []
        cols = []
        data = []
        
        for inter in interactions:
            rows.append(user_id_map[inter.user_id])
            cols.append(excursion_id_map[inter.excursion_id])
            data.append(inter.weight)
        
        interaction_matrix = csr_matrix(
            (data, (rows, cols)), 
            shape=(len(user_ids), len(excursion_ids))
        )
        
        # Train IALS model
        import implicit
        
        model = implicit.als.AlternatingLeastSquares(
            factors=settings.IALS_FACTORS,
            regularization=settings.IALS_REGULARIZATION,
            iterations=settings.IALS_ITERATIONS,
            alpha=settings.IALS_ALPHA,
            use_gpu=torch.cuda.is_available()
        )
        
        # Train model (implicit expects item-user matrix)
        item_user_matrix = interaction_matrix.T
        model.fit(item_user_matrix)
        
        # Update user profiles with IALS factors
        user_factors = model.user_factors
        item_factors = model.item_factors
        
        # Update user profiles
        for user_id, user_idx in user_id_map.items():
            user_vector = user_factors[user_idx]
            
            await db.execute(
                update(UserProfile)
                .where(UserProfile.user_id == user_id)
                .values(ials_factors=user_vector.tolist())
            )
        
        # Update excursion factors
        for excursion_id, excursion_idx in excursion_id_map.items():
            item_vector = item_factors[excursion_idx]
            
            await db.execute(
                update(Excursion)
                .where(Excursion.excursion_id == excursion_id)
                .values(ials_factors=item_vector.tolist())
            )
        
        await db.commit()
        
        logger.info("IALS model training completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"IALS model training failed: {e}")
        await db.rollback()
        return False


async def update_content_embeddings(db: AsyncSession) -> bool:
    """Update content embeddings for excursions"""
    
    try:
        logger.info("Starting content embedding updates...")
        
        # Load BERT model
        model_name = "DeepPavlov/rubert-base-cased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Get excursions that need embeddings
        result = await db.execute(
            select(Excursion).where(Excursion.has_embedding == False)
        )
        excursions = result.scalars().all()
        
        if not excursions:
            logger.info("All excursions have embeddings")
            return True
        
        # Process in batches
        batch_size = 10
        for i in range(0, len(excursions), batch_size):
            batch = excursions[i:i + batch_size]
            
            for excursion in batch:
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
                        # Use mean pooling
                        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                        embedding = embedding.numpy()
                    
                    # Update excursion
                    await db.execute(
                        update(Excursion)
                        .where(Excursion.id == excursion.id)
                        .values(
                            embedding=embedding.tolist(),
                            has_embedding=True
                        )
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for excursion {excursion.excursion_id}: {e}")
                    continue
            
            # Commit batch
            await db.commit()
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(excursions) + batch_size - 1)//batch_size}")
        
        logger.info(f"Content embeddings updated for {len(excursions)} excursions")
        return True
        
    except Exception as e:
        logger.error(f"Content embedding update failed: {e}")
        await db.rollback()
        return False


async def evaluate_recommendation_quality(
    db: AsyncSession,
    test_users: List[int] = None,
    top_k: int = 10
) -> Dict[str, float]:
    """Evaluate recommendation quality using precision@k and recall@k"""
    
    try:
        if not test_users:
            # Get users with sufficient interactions
            result = await db.execute(
                select(UserProfile.user_id)
                .where(UserProfile.interaction_count >= 5)
                .limit(100)
            )
            test_users = [row[0] for row in result.all()]
        
        if not test_users:
            return {"precision": 0.0, "recall": 0.0, "coverage": 0.0}
        
        from app.services.recommendation_engine import get_user_recommendations
        
        total_precision = 0.0
        total_recall = 0.0
        relevant_items = set()
        recommended_items = set()
        
        for user_id in test_users:
            # Get user's recent interactions (as ground truth)
            result = await db.execute(
                select(UserInteraction.excursion_id)
                .where(UserInteraction.user_id == user_id)
                .order_by(UserInteraction.timestamp.desc())
                .limit(5)
            )
            ground_truth = {row[0] for row in result.all()}
            relevant_items.update(ground_truth)
            
            # Get recommendations
            recommendations = await get_user_recommendations(db, user_id, top_k)
            recommended_ids = {rec["excursion_id"] for rec in recommendations}
            recommended_items.update(recommended_ids)
            
            # Calculate precision and recall
            if recommended_ids:
                precision = len(ground_truth & recommended_ids) / len(recommended_ids)
                total_precision += precision
            
            if ground_truth:
                recall = len(ground_truth & recommended_ids) / len(ground_truth)
                total_recall += recall
        
        # Calculate averages
        avg_precision = total_precision / len(test_users)
        avg_recall = total_recall / len(test_users)
        
        # Calculate coverage
        coverage = len(recommended_items) / len(relevant_items) if relevant_items else 0.0
        
        return {
            "precision": avg_precision,
            "recall": avg_recall,
            "coverage": coverage,
            "test_users": len(test_users)
        }
        
    except Exception as e:
        logger.error(f"Recommendation evaluation failed: {e}")
        return {"precision": 0.0, "recall": 0.0, "coverage": 0.0}
