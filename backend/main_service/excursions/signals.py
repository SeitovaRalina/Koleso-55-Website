from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Excursion


@receiver(post_save, sender=Excursion)
def vectorize_excursion_on_save(sender, instance, created, **kwargs):
    """
    Signal для запуска векторизации экскурсии при создании или обновлении
    """
    if instance.is_active:
        # Импортируем Celery приложение Django для вызова задач по имени
        from config.celery import app
        # Отправляем задачу по имени в очередь vectorizer
        app.send_task('vectorize_excursion', args=[instance.id], queue='vectorizer')
