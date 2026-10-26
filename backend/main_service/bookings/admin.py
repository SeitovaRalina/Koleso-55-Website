from django.contrib import admin, messages
from django.utils.safestring import SafeData, mark_safe
from .models import GiftCertificateRequest, TourOrder


@admin.register(GiftCertificateRequest)
class GiftCertificateRequestAdmin(admin.ModelAdmin):
    change_list_template = 'admin/bookings/giftcertificaterequest/change_list.html'
    change_form_template = 'admin/bookings/giftcertificaterequest/change_form.html'
    list_display = ('id', 'buyer_name', 'recipient_name', 'amount', 'format', 'status', 'created_at')
    list_filter = ('status', 'format', 'created_at')
    search_fields = ('buyer_name', 'buyer_phone', 'buyer_email', 'recipient_name', 'recipient_phone', 'recipient_email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Покупатель', {'fields': ('buyer_name', 'buyer_phone', 'buyer_email')}),
        ('Получатель', {'fields': ('recipient_name', 'recipient_phone', 'recipient_email')}),
        ('Сертификат', {'fields': ('amount', 'format', 'message')}),
        ('Обработка', {'fields': ('status', 'created_at', 'updated_at')}),
    )

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, {'title': 'Заявки на подарочные сертификаты', **(extra_context or {})})

    def add_view(self, request, form_url='', extra_context=None):
        return super().add_view(request, form_url, {'title': 'Создать заявку на подарочный сертификат', **(extra_context or {})})

    def change_view(self, request, object_id, form_url='', extra_context=None):
        title = f'Редактировать заявку на подарочный сертификат №{object_id}'
        return super().change_view(request, object_id, form_url, {'title': title, **(extra_context or {})})

    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        # Стандартные русские сообщения Django используют мужской род для имени модели.
        corrected = (str(message)
                     .replace('был успешно добавлен', 'успешно добавлена')
                     .replace('был успешно изменен', 'успешно изменена'))
        if isinstance(message, SafeData):
            corrected = mark_safe(corrected)
        return super().message_user(request, corrected, level, extra_tags, fail_silently)


@admin.register(TourOrder)
class TourOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'excursion', 'slot', 'full_name', 'status', 'num_participants', 'created_at']
    list_filter = ['status', 'excursion', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'slot']
