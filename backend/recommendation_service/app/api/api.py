from fastapi import APIRouter
from endpoints import recommendations
from endpoints import admin, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
