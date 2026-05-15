import requests
from django.contrib import admin, messages
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from reviews.admin import ReviewInline
from analytics.services import publish_recommendation_event
from .models import Category, Excursion, ExcursionImage, Slot


class ExcursionImageInline(admin.TabularInline):
    model = ExcursionImage
    extra = 1


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-панель для управления категориями"""
    
    list_display = ['name', 'slug', 'get_excursion_count']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def get_excursion_count(self, obj):
        """Количество экскурсий в категории"""
        return obj.excursions.count()
    get_excursion_count.short_description = _('Экскурсий')
    get_excursion_count.admin_order_field = 'excursions_count'


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    """Админ-панель для управления экскурсиями"""
    
    list_display = [
        'title', 'category', 'get_formatted_price', 'duration', 
        'get_location_type_display', 'is_active', 'get_created_at_formatted'
    ]
    list_filter = ['category', 'is_active', 'location_type', 'created_at']
    search_fields = ['title', 'description', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ExcursionImageInline, SlotInline, ReviewInline]
    
    # Массовые действия
    actions = ['activate_excursions', 'deactivate_excursions', 'retrain_recommendation_model', 'show_recommendation_stats']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'location_type')
        }),
        (_('Описание'), {
            'fields': ('short_description', 'description')
        }),
        (_('Параметры'), {
            'fields': ('price', 'duration', 'is_active')
        }),
    )
    
    def get_formatted_price(self, obj):
        """Форматированная цена с рублем"""
        return f"{obj.price:,.2f} ₽"
    get_formatted_price.short_description = _('Цена')
    get_formatted_price.admin_order_field = 'price'
    
    def get_created_at_formatted(self, obj):
        """Дата создания в русском формате"""
        return localize(obj.created_at, 'd.m.Y H:i')
    get_created_at_formatted.short_description = _('Дата создания')
    get_created_at_formatted.admin_order_field = 'created_at'
    
    def get_location_type_display(self, obj):
        """Отображаемое название типа локации"""
        return obj.get_location_type_display()
    get_location_type_display.short_description = _('Тип локации')
    get_location_type_display.admin_order_field = 'location_type'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        publish_recommendation_event(
            event_type="content_update",
            excursion_id=obj.id,
            user_id=request.user.id if request.user.is_authenticated else None,
            source="admin",
        )
    
    def activate_excursions(self, request, queryset):
        """Массовая активация экскурсий"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            _(f'Активировано {updated} экскурсий.')
        )
    activate_excursions.short_description = _('Активировать выбранные экскурсии')
    
    def deactivate_excursions(self, request, queryset):
        """Массовая деактивация экскурсий"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            _(f'Деактивировано {updated} экскурсий.')
        )
    deactivate_excursions.short_description = _('Деактивировать выбранные экскурсии')
    
    def retrain_recommendation_model(self, request, queryset):
        """Перетренировать модель рекомендаций"""
        try:
            # Вызов микросервиса для перетренировки
            response = requests.post(
                'http://recommender_api:8000/api/v1/admin/retrain',
                timeout=30
            )
            
            if response.status_code == 202:
                data = response.json()
                task_id = data.get('task_id')
                self.message_user(
                    request, 
                    _(f'Задача перетренировки модели запущена. Task ID: {task_id}'),
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    _('Ошибка при запуске перетренировки модели'),
                    messages.ERROR
                )
                
        except requests.exceptions.RequestException as e:
            self.message_user(
                request, 
                _(f'Ошибка соединения с микросервисом рекомендаций: {str(e)}'),
                messages.ERROR
            )
    
    retrain_recommendation_model.short_description = _('Перетренировать модель рекомендаций')
    
    def show_recommendation_stats(self, request, queryset):
        """Показать статистику рекомендаций"""
        try:
            # Получение статистики от микросервиса
            response = requests.get(
                'http://recommender_api:8000/api/v1/admin/stats',
                timeout=30
            )
            
            if response.status_code == 200:
                stats = response.json()
                
                # Формирование сообщения со статистикой
                stats_message = _(
                    "Статистика рекомендаций:\n"
                    f"Всего экскурсий: {stats.get('excursions', {}).get('total', 0)}\n"
                    f"С эмбеддингами: {stats.get('excursions', {}).get('with_embeddings', 0)}\n"
                    f"Пользователей: {stats.get('users', {}).get('total', 0)}\n"
                    f"Взаимодействий: {stats.get('interactions', {}).get('total', 0)}\n"
                    f"Модель готова: {'Да' if stats.get('training_state', {}).get('models_ready', False) else 'Нет'}"
                )
                
                self.message_user(request, stats_message, messages.INFO)
            else:
                self.message_user(
                    request, 
                    _('Ошибка при получении статистики рекомендаций'),
                    messages.ERROR
                )
                
        except requests.exceptions.RequestException as e:
            self.message_user(
                request, 
                _(f'Ошибка соединения с микросервисом рекомендаций: {str(e)}'),
                messages.ERROR
            )
    
    show_recommendation_stats.short_description = _('Показать статистику рекомендаций')


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    """Админ-панель для управления слотами"""
    
    list_display = [
        'excursion', 'get_date_formatted', 'get_time_formatted', 
        'max_participants', 'booked_participants', 
        'get_available_seats', 'get_availability_status'
    ]
    list_filter = ['date', 'excursion', 'excursion__category']
    search_fields = ['excursion__title']
    
    def get_date_formatted(self, obj):
        """Дата в русском формате"""
        return localize(obj.date, 'd.m.Y')
    get_date_formatted.short_description = _('Дата')
    get_date_formatted.admin_order_field = 'date'
    
    def get_time_formatted(self, obj):
        """Время в формате HH:MM"""
        return obj.time.strftime('%H:%M')
    get_time_formatted.short_description = _('Время')
    get_time_formatted.admin_order_field = 'time'
    
    def get_available_seats(self, obj):
        """Количество доступных мест"""
        return obj.available_seats
    get_available_seats.short_description = _('Доступно мест')
    get_available_seats.admin_order_field = 'available_seats'
    
    def get_availability_status(self, obj):
        """Статус доступности с цветовой индикацией"""
        if obj.is_available:
            return _('✅ Доступен')
        else:
            return _('❌ Недоступен')
    get_availability_status.short_description = _('Статус')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('excursion')
