from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _
from allauth.account.models import EmailAddress

from .models import CustomUser


try:
    admin.site.unregister(EmailAddress)
except NotRegistered:
    pass


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Админ-панель для управления пользователями"""
    
    list_display = [
        'email', 'phone', 'get_full_name_display', 
        'is_active', 'is_staff', 'get_date_joined_formatted'
    ]
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'phone', 'first_name', 'last_name')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name_display(self, obj):
        """Полное имя пользователя"""
        return obj.get_full_name()
    get_full_name_display.short_description = _('Полное имя')
    
    def get_date_joined_formatted(self, obj):
        """Дата регистрации в русском формате"""
        return localize(obj.date_joined, 'd.m.Y H:i')
    get_date_joined_formatted.short_description = _('Дата регистрации')
    get_date_joined_formatted.admin_order_field = 'date_joined'
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-date_joined')
