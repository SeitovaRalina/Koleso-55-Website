from django.contrib import admin
from .models import Review, ReviewImage, ReviewStatus
from django.utils.translation import gettext_lazy as _


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ['uploaded_at']

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['is_toxic', 'toxicity_score', 'created_at', 'updated_at', 'user', 'excursion']
    fields = ['user', 'rating', 'text', 'status', 'is_toxic', 'toxicity_score']
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'excursion', 'user', 'rating', 'status', 'is_toxic', 'created_at']
    list_filter = ['status', 'is_toxic', 'rating', 'created_at']
    search_fields = ['text', 'toxicity_score', 'user__email', 'excursion__title']
    inlines = [ReviewImageInline]

    readonly_fields = ['is_toxic', 'toxicity_score', 'created_at', 'updated_at', 'user', 'excursion']

    fieldsets = (
        (None, {
            'fields': ('excursion', 'user', 'rating', 'text')
        }),
        ('Модерация', {
            'fields': ('status', 'toxicity_score', 'moderator_comment'),
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    # ====================== Кнопки в верхней панели ======================
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        obj = self.get_object(request, object_id)
        if obj:
            extra_context['show_approve_reject'] = True
            extra_context['current_status'] = obj.status

        return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        """Обработка кастомных кнопок"""
        if "_approve_review" in request.POST:
            obj.status = ReviewStatus.APPROVED
            obj.save()
            self.message_user(request, _("Отзыв принят и опубликован."))
            return self.response_post_save_change(request, obj)

        elif "_reject_review" in request.POST:
            obj.status = ReviewStatus.REJECTED
            obj.save()
            self.message_user(request, _("Отзыв отклонён."))
            return self.response_post_save_change(request, obj)

        return super().response_change(request, obj)

    # ====================== Действия в списке ======================
    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        queryset.update(status=ReviewStatus.APPROVED)
    approve_selected.short_description = "Одобрить выбранные отзывы"

    def reject_selected(self, request, queryset):
        queryset.update(status=ReviewStatus.REJECTED)
    reject_selected.short_description = "Отклонить выбранные отзывы"
