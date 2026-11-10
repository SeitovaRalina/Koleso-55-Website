from django.db import transaction
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def claim_guest_records_by_verified_email(user):
    """Claim only unowned guest records matching a confirmed account email.

    Phone is not an identity proof: SMS verification is not configured. The
    ``user__isnull`` predicate makes repeat calls idempotent and prevents moving
    another account's records.
    """
    result = {'bookings': 0, 'inquiries': 0, 'custom_tours': 0, 'certificates': 0}
    if not user.is_email_verified or not user.email:
        return {**result, 'total': 0}

    # Import locally to avoid an accounts <-> domain-app import cycle.
    from bookings.models import CustomTourRequest, GiftCertificateRequest, TourOrder
    from excursions.models import ExcursionInquiry

    with transaction.atomic():
        result['bookings'] = TourOrder.objects.filter(
            user__isnull=True, email__iexact=user.email,
        ).update(user=user)
        result['inquiries'] = ExcursionInquiry.objects.filter(
            user__isnull=True, email__iexact=user.email,
        ).update(user=user)
        result['custom_tours'] = CustomTourRequest.objects.filter(
            user__isnull=True, email__iexact=user.email,
        ).update(user=user)
        result['certificates'] = GiftCertificateRequest.objects.filter(
            user__isnull=True, buyer_email__iexact=user.email,
        ).update(user=user)

    return {**result, 'total': sum(result.values())}

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
