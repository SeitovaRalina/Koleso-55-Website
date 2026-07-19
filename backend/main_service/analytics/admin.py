from django.contrib import admin
from .models import ExcursionView


@admin.register(ExcursionView)
class ExcursionViewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'excursion', 'session_id', 
        'duration_seconds', 'source', 'started_at', 
        'processed_for_recommendations'
    ]
    list_filter = ['source', 'processed_for_recommendations', 'started_at']
    search_fields = ['user__email', 'session_id', 'excursion__title']
    readonly_fields = ['id', 'started_at']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'excursion', 'session_id')
        }),
        ('Метрики', {
            'fields': ('duration_seconds', 'source', 'processed_for_recommendations')
        }),
        ('Временные метки', {
            'fields': ('started_at',)
        }),
    )
