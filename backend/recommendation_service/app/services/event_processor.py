import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.core.database import AsyncSessionLocal
from app.models.user import UserInteraction, UserProfile
from app.models.training import TrainingState
from app.tasks.user_profile import update_user_profile
from app.tasks.training import train_models

logger = logging.getLogger(__name__)


async def process_event(event_data: Dict[str, Any]) -> bool:
    """Process incoming event from RabbitMQ"""
    
    try:
        # Validate required fields
        required_fields = ["event_type", "item_id", "weight", "timestamp"]
        for field in required_fields:
            if field not in event_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            timestamp = datetime.utcnow()
        
        # Save interaction to database
        async with AsyncSessionLocal() as db:
            interaction = UserInteraction(
                user_id=event_data.get("user_id"),
                session_id=event_data.get("session_id"),
                excursion_id=event_data["item_id"],
                event_type=event_data["event_type"],
                weight=event_data["weight"],
                timestamp=timestamp
            )
            
            db.add(interaction)
            
            # Update training state
            result = await db.execute(select(TrainingState).limit(1))
            training_state = result.scalar_one_or_none()
            
            if not training_state:
                training_state = TrainingState()
                db.add(training_state)
            
            training_state.interactions_since_training += 1
            training_state.total_interactions += 1
            
            await db.commit()
            
            # Trigger async tasks if needed
            user_id = event_data.get("user_id")
            if user_id:
                # Update user profile
                update_user_profile.delay(user_id)
                
                # Invalidate cache
                from app.services.cache import invalidate_user_cache
                await invalidate_user_cache(user_id)
            
            # Check if retraining is needed
            if (training_state.interactions_since_training >= 
                training_state.retrain_threshold):
                logger.info(f"Triggering model training - {training_state.interactions_since_training} interactions")
                train_models.delay()
        
        logger.info(f"Processed event: {event_data['event_type']} for item {event_data['item_id']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process event: {e}")
        return False


def validate_event_weight(event_type: str, duration: int = None) -> float:
    """Validate and return appropriate weight for event type"""
    
    weight_mapping = {
        "view": 0.3,
        "long_view": 0.7,
        "favorite": 0.8,
        "review": 0.9,
        "booking": 1.0,
        "content_update": 0.0,  # Not a user interaction
        "popularity_update": 0.0  # Not a user interaction
    }
    
    base_weight = weight_mapping.get(event_type, 0.3)
    
    # Adjust weight for long views based on duration
    if event_type == "view" and duration and duration > 30:
        base_weight = 0.7  # Upgrade to long view
    
    return base_weight


async def update_excursion_popularity(excursion_id: int, bookings_count: int) -> bool:
    """Update excursion popularity from Django sync"""
    
    try:
        async with AsyncSessionLocal() as db:
            from app.models.excursion import Excursion
            
            result = await db.execute(
                update(Excursion)
                .where(Excursion.excursion_id == excursion_id)
                .values(popularity=bookings_count)
            )
            
            await db.commit()
            
            if result.rowcount > 0:
                logger.info(f"Updated popularity for excursion {excursion_id}: {bookings_count}")
                return True
            else:
                logger.warning(f"Excursion {excursion_id} not found for popularity update")
                return False
                
    except Exception as e:
        logger.error(f"Failed to update popularity for excursion {excursion_id}: {e}")
        return False
