from django.contrib import admin
from .models import GiftCertificateRequest, TourOrder


@admin.register(GiftCertificateRequest)
class GiftCertificateRequestAdmin(admin.ModelAdmin):
    change_form_template = 'admin/bookings/giftcertificaterequest/change_form.html'
    list_display = ('id', 'buyer_name', 'recipient_name', 'amount', 'format', 'created_at')
    list_filter = ('format', 'created_at')
    search_fields = ('buyer_name', 'buyer_phone', 'buyer_email', 'recipient_name', 'recipient_phone', 'recipient_email')
    readonly_fields = (
        'buyer_name', 'buyer_phone', 'buyer_email', 'recipient_name',
        'recipient_phone', 'recipient_email', 'amount', 'format',
        'message', 'created_at',
    )
    actions = None
    fieldsets = (
        ('Покупатель', {'fields': ('buyer_name', 'buyer_phone', 'buyer_email')}),
        ('Получатель', {'fields': ('recipient_name', 'recipient_phone', 'recipient_email')}),
        ('Сертификат', {'fields': ('amount', 'format', 'message')}),
        ('Поступление', {'fields': ('created_at',)}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, {'title': 'Заявки на подарочные сертификаты', **(extra_context or {})})

    def change_view(self, request, object_id, form_url='', extra_context=None):
        title = f'Просмотр заявки на подарочный сертификат №{object_id}'
        return super().change_view(request, object_id, form_url, {'title': title, **(extra_context or {})})


@admin.register(TourOrder)
class TourOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'excursion', 'slot', 'full_name', 'status', 'num_participants', 'created_at']
    list_filter = ['status', 'excursion', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'slot']
