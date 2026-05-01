from django.contrib import admin
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _

from reviews.admin import ReviewInline
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
    actions = ['activate_excursions', 'deactivate_excursions']
    
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
