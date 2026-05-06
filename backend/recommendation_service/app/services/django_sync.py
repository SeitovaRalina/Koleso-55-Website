import logging
import httpx
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.excursion import Excursion

logger = logging.getLogger(__name__)


async def sync_excursions_from_django() -> bool:
    """Sync excursion data from Django main service"""
    
    try:
        logger.info("Starting excursion sync from Django...")
        
        # Get Django API token from environment
        django_token = getattr(settings, 'DJANGO_API_TOKEN', None)
        if not django_token:
            logger.warning("No Django API token configured, using public endpoint")
        
        # Fetch all excursions from Django
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            if django_token:
                headers["Authorization"] = f"Bearer {django_token}"
            
            response = await client.get(
                f"{settings.DJANGO_BASE_URL}/api/internal/excursions/",
                headers=headers
            )
            response.raise_for_status()
            
            excursions_data = response.json()
        
        # Sync to database
        async with AsyncSessionLocal() as db:
            synced_count = 0
            updated_count = 0
            
            for excursion_data in excursions_data:
                try:
                    # Prepare data for our model
                    text_for_embedding = f"{excursion_data.get('title', '')} {excursion_data.get('description', '')} {excursion_data.get('category', '')}"
                    
                    # Check if excursion exists
                    result = await db.execute(
                        select(Excursion).where(Excursion.excursion_id == excursion_data['id'])
                    )
                    existing_excursion = result.scalar_one_or_none()
                    
                    if existing_excursion:
                        # Update existing excursion
                        await db.execute(
                            update(Excursion)
                            .where(Excursion.excursion_id == excursion_data['id'])
                            .values(
                                title=excursion_data.get('title', ''),
                                description=excursion_data.get('description', ''),
                                category=excursion_data.get('category', ''),
                                location_type=excursion_data.get('location_type', ''),
                                price=float(excursion_data.get('price', 0)),
                                duration=int(excursion_data.get('duration', 0)),
                                average_rating=excursion_data.get('average_rating'),
                                review_count=excursion_data.get('review_count', 0),
                                text_for_embedding=text_for_embedding
                            )
                        )
                        updated_count += 1
                    else:
                        # Insert new excursion
                        await db.execute(
                            insert(Excursion)
                            .values(
                                excursion_id=excursion_data['id'],
                                title=excursion_data.get('title', ''),
                                description=excursion_data.get('description', ''),
                                category=excursion_data.get('category', ''),
                                location_type=excursion_data.get('location_type', ''),
                                price=float(excursion_data.get('price', 0)),
                                duration=int(excursion_data.get('duration', 0)),
                                average_rating=excursion_data.get('average_rating'),
                                review_count=excursion_data.get('review_count', 0),
                                text_for_embedding=text_for_embedding
                            )
                        )
                        synced_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to sync excursion {excursion_data.get('id')}: {e}")
                    continue
            
            await db.commit()
            
            logger.info(f"Excursion sync completed: {synced_count} new, {updated_count} updated")
            
            # Trigger embedding generation for new excursions
            if synced_count > 0:
                from app.tasks.embeddings import generate_embeddings_for_excursions
                generate_embeddings_for_excursions.delay()
            
            return True
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error syncing from Django: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to sync excursions from Django: {e}")
        return False


async def sync_popularity_from_django() -> bool:
    """Sync popularity data from Django"""
    
    try:
        logger.info("Syncing popularity data from Django...")
        
        # Get popularity data from Django
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            django_token = getattr(settings, 'DJANGO_API_TOKEN', None)
            if django_token:
                headers["Authorization"] = f"Bearer {django_token}"
            
            response = await client.get(
                f"{settings.DJANGO_BASE_URL}/api/internal/popularity/",
                headers=headers
            )
            response.raise_for_status()
            
            popularity_data = response.json()  # {excursion_id: bookings_count}
        
        # Update popularity in database
        async with AsyncSessionLocal() as db:
            updated_count = 0
            
            for excursion_id, bookings_count in popularity_data.items():
                try:
                    await db.execute(
                        update(Excursion)
                        .where(Excursion.excursion_id == int(excursion_id))
                        .values(popularity=int(bookings_count))
                    )
                    updated_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to update popularity for excursion {excursion_id}: {e}")
                    continue
            
            await db.commit()
            
            logger.info(f"Popularity sync completed: {updated_count} excursions updated")
            return True
            
    except Exception as e:
        logger.error(f"Failed to sync popularity from Django: {e}")
        return False


async def get_single_excursion_from_django(excursion_id: int) -> Dict[str, Any]:
    """Get single excursion data from Django"""
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            django_token = getattr(settings, 'DJANGO_API_TOKEN', None)
            if django_token:
                headers["Authorization"] = f"Bearer {django_token}"
            
            response = await client.get(
                f"{settings.DJANGO_BASE_URL}/api/internal/excursions/{excursion_id}/",
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"Excursion {excursion_id} not found in Django")
            return {}
        raise
    except Exception as e:
        logger.error(f"Failed to get excursion {excursion_id} from Django: {e}")
        return {}


async def test_django_connection() -> bool:
    """Test connection to Django service"""
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.DJANGO_BASE_URL}/api/health/")
            response.raise_for_status()
            
            logger.info("Django connection test successful")
            return True
            
    except Exception as e:
        logger.error(f"Django connection test failed: {e}")
        return False
