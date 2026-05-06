import logging
import sys


def setup_logging():
    """Setup logging configuration"""
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Set specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aio_pika").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
