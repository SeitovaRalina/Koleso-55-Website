from typing import Annotated

from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import get_db
from app.services.cache import CacheService
from app.services.content import ContentService
from app.services.collaborative import CollaborativeService
from app.services.hybrid import HybridService
from app.services.django_client import DjangoClient


def get_settings(request: Request) -> Settings:
    """Get settings from app.state"""
    return request.app.state.settings


def get_django_client(request: Request) -> DjangoClient:
    """Get Django API client from app.state"""
    return request.app.state.django_client

def get_cache_service(request: Request) -> CacheService:
    """Get cache service instance from app.state"""
    return request.app.state.cache_service

def get_content_service(
    settings: Annotated[Settings, Depends(get_settings)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
    db: AsyncSession = Depends(get_db)
) -> ContentService:
    """Get content-based service instance"""
    return ContentService(db, settings, cache_service)


def get_collaborative_service(
    settings: Annotated[Settings, Depends(get_settings)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
    db: AsyncSession = Depends(get_db)
) -> CollaborativeService:
    """Get collaborative filtering service instance"""
    return CollaborativeService(db, settings, cache_service)


def get_hybrid_service(
    settings: Annotated[Settings, Depends(get_settings)],
    collaborative_service: Annotated[CollaborativeService, Depends(get_collaborative_service)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
    django_client: Annotated[DjangoClient, Depends(get_django_client)],
    db: AsyncSession = Depends(get_db)
) -> HybridService:
    """Get hybrid recommendation service instance"""
    return HybridService(db, settings, collaborative_service, cache_service, django_client)
