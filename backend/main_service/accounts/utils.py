from django.db import transaction
from bookings.models import TourOrder
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def link_guest_bookings(user):
    """
    Привязывает гостевые бронирования к пользователю по совпадению email или телефона.
    Также заполняет профиль пользователя данными из последнего бронирования.
    
    Гостевые заявки привязываются один раз - при регистрации или изменении контактов.
    Уже привязанные заявки остаются с аккаунтом навсегда.
    """
    if not user.email and not user.phone:
        return {'linked': 0, 'profile_updated': False}
    
    linked_count = 0
    profile_updated = False
    
    # Ищем гостевые бронирования (user is null) с совпадающим email или телефоном
    guest_bookings = TourOrder.objects.filter(user__isnull=True)
    
    # Используем select_for_update() чтобы избежать блокировки всей таблицы
    with transaction.atomic():
        if user.email:
            guest_bookings_email = guest_bookings.filter(email__iexact=user.email)
            linked_email = guest_bookings_email.update(user=user)
            linked_count += linked_email
        
        if user.phone:
            guest_bookings_phone = guest_bookings.filter(phone=user.phone)
            linked_phone = guest_bookings_phone.update(user=user)
            linked_count += linked_phone
        
        # Если профиль пользователя не заполнен, заполняем из последнего бронирования
        if (not user.first_name or not user.last_name) and linked_count > 0:
            latest_booking = TourOrder.objects.filter(
                user=user
            ).order_by('-created_at').first()
            
            if latest_booking:
                if not user.first_name and latest_booking.first_name:
                    user.first_name = latest_booking.first_name
                    profile_updated = True
                
                if not user.last_name and latest_booking.last_name:
                    user.last_name = latest_booking.last_name
                    profile_updated = True
                
                if profile_updated:
                    user.save(update_fields=['first_name', 'last_name'])
    
    return {
        'linked': linked_count,
        'profile_updated': profile_updated
    }

def get_domain_and_protocol(request=None):
    """Получение домена и протокола из запроса или settings"""
    if request:
        domain = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
    else:
        domain = getattr(settings, 'DOMAIN', 'localhost:8000')
        protocol = getattr(settings, 'PROTOCOL', 'http')
    return domain, protocol

def format_user_data(user):
    """Форматирует данные пользователя в едином стиле"""
    return {
        'id': user.id,
        'email': user.email,
        'phone': user.phone,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'patronymic': user.patronymic,
        'is_email_verified': user.is_email_verified,
        'full_name': user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name} {user.last_name}".strip(),
    }


def generate_jwt_response(user):
    """Генерирует JWT токены и форматирует ответ"""
    refresh = RefreshToken.for_user(user)
    return {
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'user': format_user_data(user),
    }
