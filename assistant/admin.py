from django.contrib import admin
from assistant.models import (
    DialogCategory, ExcursionCategory, Client, 
    Excursion, ChatMessage, ChatState, LeadRequest
)

@admin.register(DialogCategory)
class DialogCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')

@admin.register(ExcursionCategory)
class ExcursionCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'phone', 'external_id')
    search_fields = ('phone', 'first_name', 'external_id')

@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_from', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('title',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('client', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Сообщение'

@admin.register(ChatState)
class ChatStateAdmin(admin.ModelAdmin):
    list_display = ('client', 'category', 'date', 'budget', 'created_at')
    list_filter = ('created_at',)

@admin.register(LeadRequest)
class LeadRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'excursion', 'get_client_name', 'get_client_phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')

    def get_client_name(self, obj):
        return obj.chat_state.client.first_name or "Без имени"
    get_client_name.short_description = 'Имя клиента'

    def get_client_phone(self, obj):
        return obj.chat_state.client.phone or "Нет телефона"
    get_client_phone.short_description = 'Телефон клиента'