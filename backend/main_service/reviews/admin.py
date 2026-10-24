from django.contrib import admin
from django import forms
from django.utils.formats import localize
from django.utils.translation import gettext_lazy as _

from .models import Review, ReviewImage, ReviewStatus


class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        if self.instance.pk is None:
            self.instance.is_admin_added = True
            self.instance.user = None
            cleaned['manual_first_name'] = (cleaned.get('manual_first_name') or '').strip()
            cleaned['manual_last_name'] = (cleaned.get('manual_last_name') or '').strip()
            for field in ('manual_first_name', 'manual_last_name'):
                if not cleaned[field]:
                    self.add_error(field, _('Обязательное поле.'))

        if self.instance.is_admin_added and all(
            cleaned.get(field) for field in ('excursion', 'manual_first_name', 'manual_last_name', 'rating', 'text')
        ):
            duplicate = Review.objects.filter(
                is_admin_added=True,
                excursion=cleaned['excursion'],
                manual_first_name__iexact=cleaned['manual_first_name'],
                manual_last_name__iexact=cleaned['manual_last_name'],
                rating=cleaned['rating'],
                text=cleaned['text'],
            ).exclude(pk=self.instance.pk).exists()
            if duplicate:
                raise forms.ValidationError(_('Такой ручной отзыв уже существует.'))
        return cleaned


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ['uploaded_at']
    fields = ['image', 'is_homepage_main', 'homepage_order', 'uploaded_at']


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['is_toxic', 'toxicity_score', 'created_at', 'updated_at', 'author_name', 'user', 'excursion']
    fields = ['author_name', 'rating', 'text', 'status', 'is_toxic', 'toxicity_score']
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin panel for excursion reviews."""

    list_display = [
        'id', 'excursion', 'author_name', 'is_admin_added', 'rating', 'status',
        'is_toxic', 'show_on_homepage', 'homepage_order', 'get_created_at_formatted',
    ]
    list_filter = ['status', 'show_on_homepage', 'is_toxic', 'rating', 'created_at']
    search_fields = ['text', 'user__email', 'manual_first_name', 'manual_last_name', 'excursion__title']
    inlines = [ReviewImageInline]
    form = ReviewAdminForm
    readonly_fields = ['is_toxic', 'toxicity_score', 'created_at', 'updated_at', 'user', 'is_admin_added']

    fieldsets = (
        (None, {
            'fields': ('excursion', 'user', 'rating', 'text'),
        }),
        ('Главная страница', {
            'fields': (
                'show_on_homepage',
                'homepage_author_name',
                'homepage_order',
            ),
            'description': 'Отмеченные одобренные отзывы показываются на главной. Главное фото выбирается в блоке "Фото к отзывам": сначала фото с галочкой, затем по порядку.',
        }),
        ('Модерация', {
            'fields': ('status', 'toxicity_score', 'moderator_comment'),
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (("Отзыв клиента (добавлен администратором)", {
                'fields': ('manual_first_name', 'manual_last_name', 'excursion', 'rating', 'text'),
                'description': 'Вносите только настоящий отзыв, полученный вне сайта. После сохранения он ожидает модерации.',
            }),)
        author_fields = ('manual_first_name', 'manual_last_name') if obj.is_admin_added else ('user',)
        return (
            (None, {'fields': ('excursion', *author_fields, 'rating', 'text')}),
            *self.fieldsets[1:],
        )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            fields.append('excursion')
        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_admin_added = True
            obj.user = None
            obj.status = ReviewStatus.PENDING
        super().save_model(request, obj, form, change)

    actions = [
        'approve_selected',
        'reject_selected',
        'show_on_homepage_selected',
        'hide_from_homepage_selected',
    ]

    def get_created_at_formatted(self, obj):
        return localize(obj.created_at, 'd.m.Y H:i')

    get_created_at_formatted.short_description = _('Дата создания')
    get_created_at_formatted.admin_order_field = 'created_at'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['show_approve_reject'] = True
            extra_context['current_status'] = obj.status
        return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        if "_approve_review" in request.POST:
            obj.status = ReviewStatus.APPROVED
            obj.save()
            self.message_user(request, _("Отзыв принят и опубликован."))
            return self.response_post_save_change(request, obj)

        if "_reject_review" in request.POST:
            obj.status = ReviewStatus.REJECTED
            obj.save()
            self.message_user(request, _("Отзыв отклонен."))
            return self.response_post_save_change(request, obj)

        return super().response_change(request, obj)

    def approve_selected(self, request, queryset):
        queryset.update(status=ReviewStatus.APPROVED)

    approve_selected.short_description = "Одобрить выбранные отзывы"

    def reject_selected(self, request, queryset):
        queryset.update(status=ReviewStatus.REJECTED)

    reject_selected.short_description = "Отклонить выбранные отзывы"

    def show_on_homepage_selected(self, request, queryset):
        queryset.update(show_on_homepage=True)

    show_on_homepage_selected.short_description = "Показывать выбранные отзывы на главной"

    def hide_from_homepage_selected(self, request, queryset):
        queryset.update(show_on_homepage=False)

    hide_from_homepage_selected.short_description = "Скрыть выбранные отзывы с главной"
