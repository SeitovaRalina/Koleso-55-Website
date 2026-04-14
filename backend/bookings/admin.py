from django.contrib import admin
from .models import TourOrder


@admin.register(TourOrder)
class TourOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'excursion', 'slot', 'full_name', 'status', 'num_participants', 'created_at']
    list_filter = ['status', 'excursion', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'slot']
