from django.contrib import admin
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Админ-панель для управления избранным"""
    
    list_display = ['user', 'excursion', 'added_at']
    list_filter = ['added_at', 'excursion__category']
    search_fields = [
        'user__email', 
        'user__first_name', 
        'user__last_name',
        'excursion__title'
    ]
    readonly_fields = ['added_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'excursion')
        }),
        ('Дополнительно', {
            'fields': ('added_at',),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 
            'excursion__category'
        )
