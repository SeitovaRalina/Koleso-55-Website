from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TrainingStatusResponse(BaseModel):
    """Training status response"""
    models_ready: bool = Field(..., description="Whether ML models are ready")
    last_training_time: Optional[datetime] = Field(None, description="Last training timestamp")
    total_interactions: int = Field(..., ge=0, description="Total interactions processed")
    interactions_since_training: int = Field(..., ge=0, description="Interactions since last training")
    retrain_threshold: int = Field(..., ge=1, description="Threshold for automatic retraining")


class RetrainResponse(BaseModel):
    """Retraining response"""
    status: str = Field(..., description="Status: started, skipped, or error")
    message: Optional[str] = Field(None, description="Status message")
    reason: Optional[str] = Field(None, description="Reason for skipping")
    interactions_since_training: Optional[int] = Field(None, description="Current interaction count")
    threshold: Optional[int] = Field(None, description="Retraining threshold")


class SyncResponse(BaseModel):
    """Sync response"""
    status: str = Field(..., description="Status: started or error")
    message: Optional[str] = Field(None, description="Status message")


class CacheStatsResponse(BaseModel):
    """Cache statistics response"""
    total_keys: int = Field(..., ge=0, description="Total Redis keys")
    user_cache_keys: int = Field(..., ge=0, description="User recommendation cache keys")
    similar_cache_keys: int = Field(..., ge=0, description="Similar items cache keys")
    memory_usage: str = Field(..., description="Memory usage in human readable format")
    connected_clients: int = Field(..., ge=0, description="Number of connected Redis clients")


class EvaluationResponse(BaseModel):
    """Model evaluation response"""
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision@K score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall@K score")
    coverage: float = Field(..., ge=0.0, le=1.0, description="Catalog coverage")
    test_users: int = Field(..., ge=0, description="Number of users in test set")
