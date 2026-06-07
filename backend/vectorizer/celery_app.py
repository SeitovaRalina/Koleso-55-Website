import os
from celery import Celery
 
# Создаем экземпляр Celery
app = Celery('vectorizer')
 
# Настраиваем broker и backend из переменных окружения
app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672/'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'vectorize_excursion': {'queue': 'vectorizer'},
    },
    # Включаем автодискавери задач из текущего модуля
    include=['tasks'],
)
 
 
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')