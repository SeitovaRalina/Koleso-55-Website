from pydantic import BaseModel, Field
from typing import Optional


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status: ok, degraded, or error")
    models_ready: bool = Field(..., description="Whether ML models are ready")
    db_connected: bool = Field(..., description="Database connection status")
    rabbitmq_connected: bool = Field(..., description="RabbitMQ connection status")
    redis_connected: bool = Field(..., description="Redis connection status")


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with additional info"""
    service: str = Field(default="recommendation-api", description="Service name")
    uptime_seconds: Optional[int] = Field(None, description="Service uptime in seconds")
    version: str = Field(default="1.0.0", description="Service version")
