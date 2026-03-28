from django.contrib import admin
from .models import Category, Excursion, ExcursionImage, Slot


class ExcursionImageInline(admin.TabularInline):
    model = ExcursionImage
    extra = 1


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'duration', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ExcursionImageInline, SlotInline]


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ['excursion', 'date', 'time', 'available_seats', 'is_available']
    list_filter = ['date', 'excursion']