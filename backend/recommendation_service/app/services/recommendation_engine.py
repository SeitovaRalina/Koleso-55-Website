import numpy as np
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.config import settings
from app.models.user import UserProfile, UserInteraction
from app.models.excursion import Excursion
from app.models.cache import RecommendationCache, SimilarCache

logger = logging.getLogger(__name__)


async def get_user_recommendations(
    db: AsyncSession,
    user_id: int,
    top_k: int = 20,
    exclude_interacted: bool = True
) -> List[Dict[str, Any]]:
    """Get personalized recommendations for a user using hybrid approach"""
    
    try:
        # Get user profile
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = result.scalar_one_or_none()
        
        # Cold start: return popular items if user has insufficient interactions
        if (not user_profile or 
            user_profile.interaction_count < settings.COLD_START_MIN_INTERACTIONS):
            return await get_popular_excursions(db, top_k)
        
        # Get excursions with embeddings and IALS factors
        result = await db.execute(
            select(Excursion).where(
                and_(
                    Excursion.has_embedding == True,
                    Excursion.embedding.isnot(None),
                    Excursion.ials_factors.isnot(None)
                )
            )
        )
        excursions = result.scalars().all()
        
        if not excursions:
            logger.warning("No excursions with embeddings found")
            return await get_popular_excursions(db, top_k)
        
        # Get user's interacted excursions for exclusion
        interacted_excursions = set()
        if exclude_interacted:
            result = await db.execute(
                select(UserInteraction.excursion_id).where(
                    UserInteraction.user_id == user_id
                )
            )
            interacted_excursions = {row[0] for row in result.all()}
        
        # Calculate recommendation scores
        recommendations = []
        max_popularity = max(exc.popularity for exc in excursions) if excursions else 1
        
        for excursion in excursions:
            # Skip if user already interacted with this excursion
            if exclude_interacted and excursion.excursion_id in interacted_excursions:
                continue
            
            # Calculate content similarity
            content_score = 0.0
            if user_profile.content_vector and excursion.embedding:
                content_score = cosine_similarity(
                    np.array(user_profile.content_vector),
                    np.array(excursion.embedding)
                )
            
            # Calculate collaborative filtering score
            collab_score = 0.0
            if user_profile.ials_factors and excursion.ials_factors:
                collab_score = np.dot(
                    np.array(user_profile.ials_factors),
                    np.array(excursion.ials_factors)
                )
            
            # Calculate popularity score
            popularity_score = excursion.popularity / max_popularity if max_popularity > 0 else 0
            
            # Hybrid score
            final_score = (
                settings.HYBRID_ALPHA * content_score +
                (1 - settings.HYBRID_ALPHA - settings.POPULARITY_WEIGHT) * collab_score +
                settings.POPULARITY_WEIGHT * popularity_score
            )
            
            recommendations.append({
                "excursion_id": excursion.excursion_id,
                "score": float(final_score),
                "breakdown": {
                    "content": float(content_score),
                    "collab": float(collab_score),
                    "popularity": float(popularity_score)
                }
            })
        
        # Sort by score and take top_k
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_k]
        
    except Exception as e:
        logger.error(f"Error getting user recommendations: {e}")
        return await get_popular_excursions(db, top_k)


async def get_similar_excursions(
    db: AsyncSession,
    excursion_id: int,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """Get similar excursions based on content and collaborative factors"""
    
    try:
        # Get the target excursion
        result = await db.execute(
            select(Excursion).where(Excursion.excursion_id == excursion_id)
        )
        target_excursion = result.scalar_one_or_none()
        
        if not target_excursion:
            return []
        
        # Get other excursions with embeddings
        result = await db.execute(
            select(Excursion).where(
                and_(
                    Excursion.excursion_id != excursion_id,
                    Excursion.has_embedding == True,
                    Excursion.embedding.isnot(None)
                )
            )
        )
        excursions = result.scalars().all()
        
        if not excursions:
            return []
        
        # Calculate similarity scores
        similarities = []
        
        for excursion in excursions:
            # Content similarity
            content_sim = 0.0
            if target_excursion.embedding and excursion.embedding:
                content_sim = cosine_similarity(
                    np.array(target_excursion.embedding),
                    np.array(excursion.embedding)
                )
            
            # Category bonus (same category gets boost)
            category_bonus = 0.2 if target_excursion.category == excursion.category else 0.0
            
            # Combined similarity
            combined_sim = content_sim + category_bonus
            
            similarities.append({
                "excursion_id": excursion.excursion_id,
                "score": float(combined_sim),
                "content_similarity": float(content_sim),
                "category_bonus": float(category_bonus)
            })
        
        # Sort by similarity and take top_k
        similarities.sort(key=lambda x: x["score"], reverse=True)
        return similarities[:top_k]
        
    except Exception as e:
        logger.error(f"Error getting similar excursions: {e}")
        return []


async def get_popular_excursions(
    db: AsyncSession,
    top_k: int = 20,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get popular excursions for cold start"""
    
    try:
        query = select(Excursion).where(Excursion.has_embedding == True)
        
        if category:
            query = query.where(Excursion.category == category)
        
        query = query.order_by(Excursion.popularity.desc()).limit(top_k)
        
        result = await db.execute(query)
        excursions = result.scalars().all()
        
        return [
            {
                "excursion_id": exc.excursion_id,
                "title": exc.title,
                "category": exc.category,
                "popularity": exc.popularity,
                "average_rating": exc.average_rating,
                "score": 1.0  # Popular items get score of 1.0
            }
            for exc in excursions
        ]
        
    except Exception as e:
        logger.error(f"Error getting popular excursions: {e}")
        return []


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))
