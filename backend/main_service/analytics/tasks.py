import json
from celery import shared_task
from django.conf import settings
import pika


@shared_task(bind=True, max_retries=3)
def publish_event(self, event_data):
    """
    Публикует событие в RabbitMQ exchange 'excursion_events'
    с routing_key 'excursion_events'
    """
    try:
        # Устанавливаем соединение с RabbitMQ
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.CELERY_BROKER_URL)
        )
        channel = connection.channel()
        
        # Объявляем exchange (если не существует)
        channel.exchange_declare(
            exchange='excursion_events',
            exchange_type='topic',
            durable=True
        )
        
        # Объявляем очередь (если не существует)
        channel.queue_declare(
            queue='excursion_events',
            durable=True
        )
        
        # Привязываем очередь к exchange
        channel.queue_bind(
            exchange='excursion_events',
            queue='excursion_events',
            routing_key='excursion_events'
        )
        
        # Публикуем сообщение
        channel.basic_publish(
            exchange='excursion_events',
            routing_key='excursion_events',
            body=json.dumps(event_data, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Делаем сообщение постоянным
                content_type='application/json'
            )
        )
        
        connection.close()
        
    except Exception as exc:
        # Повторная попытка в случае ошибки
        raise self.retry(exc=exc, countdown=60)
