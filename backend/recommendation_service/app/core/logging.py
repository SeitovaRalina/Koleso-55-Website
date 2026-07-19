import logging
import sys
import time
import uuid
from typing import Dict, Any
from contextvars import ContextVar

import structlog
from fastapi import Request, Response
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware


request_id: ContextVar[str] = ContextVar('request_id')
user_id: ContextVar[str] = ContextVar('user_id')
session_id: ContextVar[str] = ContextVar('session_id')


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging with duration tracking"""

    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        request_id.set(req_id)

        user_id.set(request.headers.get("X-User-ID", "anonymous"))
        session_id.set(request.headers.get("X-Session-ID", "none"))

        start_time = time.time()

        logger = structlog.get_logger()
        logger.info(
            "request_started",
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("User-Agent", "unknown"),
            request_id=req_id,
            user_id=user_id.get(),
            session_id=session_id.get()
        )

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            logger.info(
                "request_completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
                request_id=req_id,
                user_id=user_id.get(),
                session_id=session_id.get()
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = req_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request error
            logger.error(
                "request_failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration=duration,
                request_id=req_id,
                user_id=user_id.get(),
                session_id=session_id.get(),
                exc_info=True
            )
            
            # Re-raise exception
            raise


def setup_logging():
    """Configure structured logging for the application"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_request_context,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def add_request_context(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request context to log records"""
    # Add request ID if available
    req_id = request_id.get(None)
    if req_id:
        event_dict["request_id"] = req_id
    
    # Add user ID if available
    uid = user_id.get(None)
    if uid:
        event_dict["user_id"] = uid
    
    # Add session ID if available
    sid = session_id.get(None)
    if sid:
        event_dict["session_id"] = sid
    
    return event_dict


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


# Training-specific logging helpers
# TODOL: НИГДЕ НЕ ИСПОЛЬЗУЕТСЯ, ИСПРАВИТЬ
def log_training_start(user_count: int, item_count: int, interaction_count: int):
    """Log training start with metrics"""
    logger = get_logger("training")
    logger.info(
        "training_started",
        user_count=user_count,
        item_count=item_count,
        interaction_count=interaction_count
    )


def log_training_end(
    duration: float, 
    iterations: int, 
    final_loss: float,
    factors: int
):
    """Log training completion with metrics"""
    logger = get_logger("training")
    logger.info(
        "training_completed",
        duration=duration,
        iterations=iterations,
        final_loss=final_loss,
        factors=factors
    )


def log_cache_operation(
    operation: str, 
    cache_type: str, 
    key: str, 
    hit: bool = None,
    ttl: int = None
):
    """Log cache operations"""
    logger = get_logger("cache")
    logger.info(
        "cache_operation",
        operation=operation,
        cache_type=cache_type,
        key=key,
        hit=hit,
        ttl=ttl
    )


def log_recommendation_request(
    user_id: int,
    algorithm: str,
    items_returned: int,
    cache_hit: bool,
    duration: float
):
    """Log recommendation request details"""
    logger = get_logger("recommendations")
    logger.info(
        "recommendation_request",
        user_id=user_id,
        algorithm=algorithm,
        items_returned=items_returned,
        cache_hit=cache_hit,
        duration=duration
    )


def log_model_prediction(
    user_id: int,
    item_id: int,
    algorithm: str,
    score: float,
    components: Dict[str, float] = None
):
    """Log model prediction details"""
    logger = get_logger("prediction")
    logger.info(
        "model_prediction",
        user_id=user_id,
        item_id=item_id,
        algorithm=algorithm,
        score=score,
        components=components or {}
    )
