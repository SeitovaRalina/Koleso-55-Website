from django.contrib import admin
from .models import GiftCertificateRequest, TourOrder


@admin.register(GiftCertificateRequest)
class GiftCertificateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'recipient_name', 'amount', 'format', 'status', 'created_at')
    list_filter = ('status', 'format', 'created_at')
    search_fields = ('buyer_name', 'buyer_phone', 'buyer_email', 'recipient_name', 'recipient_phone', 'recipient_email')
    readonly_fields = (
        'buyer_name', 'buyer_phone', 'buyer_email', 'recipient_name', 'recipient_phone',
        'recipient_email', 'amount', 'format', 'message', 'created_at', 'updated_at',
    )


@admin.register(TourOrder)
class TourOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'excursion', 'slot', 'full_name', 'status', 'num_participants', 'created_at']
    list_filter = ['status', 'excursion', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'slot']
