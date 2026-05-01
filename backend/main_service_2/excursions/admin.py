from django.contrib import admin
from .models import User, Excursion, UserExcursion


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'created_at']
    search_fields = ['username', 'email']


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'duration', 'price', 'is_active', 'created_at']
    search_fields = ['title', 'location']
    list_filter = ['is_active', 'created_at']


@admin.register(UserExcursion)
class UserExcursionAdmin(admin.ModelAdmin):
    list_display = ['user', 'excursion', 'visited_at']
    search_fields = ['user__username', 'excursion__title']
    list_filter = ['visited_at']
