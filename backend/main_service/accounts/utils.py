from django.db import transaction
from .models import CustomUser
from bookings.models import TourOrder


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
