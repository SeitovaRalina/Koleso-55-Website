import os
from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_id, domain, protocol='http'):
    """
    Отправляет письмо подтверждения email пользователю.
    
    Args:
        user_id: ID пользователя
        domain: домен сайта (например, 'example.com')
        protocol: протокол ('http' или 'https')
    """
    try:
        user = User.objects.get(pk=user_id)
        
        # Проверяем, не подтвержден ли уже email
        if user.is_email_verified:
            return f"Email для пользователя {user.email} уже подтвержден"
        
        # Проверяем, не проходило ли 24 часа с последней отправки
        if user.email_verification_sent_at:
            time_since_last_sent = timezone.now() - user.email_verification_sent_at
            if time_since_last_sent < timedelta(hours=24):
                return f"Письмо подтверждения уже отправлялось менее 24 часов назад для {user.email}"
        
        # Генерируем токен и uidb64
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Строим URL подтверждения
        verify_url = f"{protocol}://{domain}/api/accounts/verify-email/{uidb64}/{token}/"
        
        # Тема и тело письма
        subject = 'Подтверждение email - КОЛЕСО путешествий 55'
        message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Спасибо за регистрацию на сайте «КОЛЕСО путешествий 55».

Для подтверждения вашего email адреса, пожалуйста, перейдите по следующей ссылке:
{verify_url}

Эта ссылка действительна в течение 24 часов.

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Команда «КОЛЕСО путешествий 55»
"""
        
        # Отправляем письмо
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@koleso55.ru'),
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        # Обновляем время отправки
        user.email_verification_sent_at = timezone.now()
        user.save(update_fields=['email_verification_sent_at'])
        
        return f"Письмо подтверждения успешно отправлено на {user.email}"
        
    except User.DoesNotExist:
        return f"Пользователь с ID {user_id} не найден"
    except Exception as exc:
        # Retry logic with exponential backoff
        retry_delay = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=retry_delay)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, user_id, domain, protocol='http'):
    """
    Отправляет письмо для сброса пароля.
    
    Args:
        user_id: ID пользователя
        domain: домен сайта
        protocol: протокол ('http' или 'https')
    """
    try:
        user = User.objects.get(pk=user_id)
        
        # Генерируем токен и uidb64
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Строим URL сброса пароля
        reset_url = f"{protocol}://{domain}/api/accounts/password-reset-confirm/{uidb64}/{token}/"
        
        # Тема и тело письма
        subject = 'Сброс пароля - КОЛЕСО путешествий 55'
        message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Вы получили это письмо, потому что был запрошен сброс пароля для вашего аккаунта.

Для сброса пароля, пожалуйста, перейдите по следующей ссылке:
{reset_url}

Эта ссылка действительна в течение 24 часов.

Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.

С уважением,
Команда «КОЛЕСО путешествий 55»
"""
        
        # Отправляем письмо
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@koleso55.ru'),
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return f"Письмо для сброса пароля успешно отправлено на {user.email}"
        
    except User.DoesNotExist:
        return f"Пользователь с ID {user_id} не найден"
    except Exception as exc:
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_delay)
