from django.contrib import admin
from .models import Review, ReviewImage, ReviewStatus


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'excursion', 'user', 'rating', 'status', 'is_toxic', 'created_at']
    list_filter = ['status', 'is_toxic', 'rating', 'created_at']
    search_fields = ['text', 'toxicity_score', 'user__email', 'excursion__title']
    inlines = [ReviewImageInline]

    readonly_fields = ['is_toxic', 'toxicity_score']

    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        queryset.update(status=ReviewStatus.APPROVED)
    approve_selected.short_description = "Одобрить выбранные отзывы"

    def reject_selected(self, request, queryset):
        queryset.update(status=ReviewStatus.REJECTED)
    reject_selected.short_description = "Отклонить выбранные отзывы"
