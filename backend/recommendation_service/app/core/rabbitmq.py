import asyncio
import json
import logging
from typing import Dict, Any
import aio_pika
from aio_pika import ExchangeType, Message

from app.core.config import settings
from app.services.event_processor import process_event

logger = logging.getLogger(__name__)


async def rabbitmq_consumer():
    """RabbitMQ consumer for excursion events"""
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            # Connect to RabbitMQ
            connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                heartbeat=60
            )
            
            logger.info("Connected to RabbitMQ")
            
            # Create channel
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            
            # Declare exchange
            exchange = await channel.declare_exchange(
                "excursion_events",
                ExchangeType.TOPIC,
                durable=True
            )
            
            # Declare queue
            queue = await channel.declare_queue(
                settings.RABBITMQ_QUEUE,
                durable=True
            )
            
            # Bind queue to exchange
            await queue.bind(exchange, routing_key="excursion_events")
            
            logger.info(f"RabbitMQ consumer ready, queue: {settings.RABBITMQ_QUEUE}")
            
            # Start consuming
            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        event_data = json.loads(message.body.decode())
                        await process_event(event_data)
                        logger.debug(f"Processed event: {event_data.get('event_type')}")
                    except Exception as e:
                        logger.error(f"Failed to process message: {e}")
                        raise  # This will trigger NACK and retry
            
            await queue.consume(message_handler)
            
            # Keep the consumer running
            await asyncio.Future()
            
        except Exception as e:
            retry_count += 1
            logger.error(f"RabbitMQ connection failed (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                await asyncio.sleep(5 * retry_count)  # Exponential backoff
            else:
                logger.error("Max retries reached, giving up")
                break


async def publish_event(event_data: Dict[str, Any]):
    """Publish event to RabbitMQ (for testing/admin purposes)"""
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()
        
        exchange = await channel.declare_exchange(
            "excursion_events",
            ExchangeType.TOPIC,
            durable=True
        )
        
        message = Message(
            body=json.dumps(event_data).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        await exchange.publish(message, routing_key="excursion_events")
        await connection.close()
        
        logger.info(f"Published event: {event_data.get('event_type')}")
        
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        raise
