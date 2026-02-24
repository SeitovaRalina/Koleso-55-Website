from django.contrib import admin
from .models import Category, Excursion, ExcursionSlot


class ExcursionSlotInline(admin.TabularInline):
    model = ExcursionSlot
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "vk_id")
    search_fields = ("title",)


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("title",)
    inlines = [ExcursionSlotInline]