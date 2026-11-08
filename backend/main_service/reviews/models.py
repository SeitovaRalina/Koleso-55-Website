from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from excursions.models import Excursion
from bookings.models import TourOrder


class ReviewStatus(models.TextChoices):
    PENDING = 'pending', _('На модерации')
    APPROVED = 'approved', _('Одобрен')
    REJECTED = 'rejected', _('Отклонён')


class Review(models.Model):
    """Модель отзыва на экскурсию"""
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name=_('Пользователь'),
        help_text=_('Автор отзыва')
    )
    is_admin_added = models.BooleanField(_('Добавлен администратором'), default=False, editable=False)
    manual_first_name = models.CharField(_('Имя автора'), max_length=150, blank=True)
    manual_last_name = models.CharField(_('Фамилия автора'), max_length=150, blank=True)
    excursion = models.ForeignKey(
        Excursion, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name=_('Экскурсия'),
        help_text=_('Экскурсия, на которую оставлен отзыв')
    )
    order = models.ForeignKey(
        TourOrder, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Заказ'),
        help_text=_('Заказ, по которому оставлен отзыв')
    )

    rating = models.PositiveSmallIntegerField(
        _('Оценка'), 
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text=_('Оценка экскурсии от 1 до 5 звезд')
    )
    text = models.TextField(
        _('Отзыв'), 
        max_length=2000,
        help_text=_('Текст отзыва на экскурсию')
    )

    status = models.CharField(
        _('Статус модерации'),
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        help_text=_('Текущий статус модерации отзыва')
    )
    is_toxic = models.BooleanField(
        _('Содержит нецензурную лексику'), 
        default=False,
        help_text=_('Определяет, содержит ли отзыв нецензурную лексику')
    )
    toxicity_score = models.FloatField(
        _('Степень токсичности'), 
        default=0.0,
        help_text=_('Количественная оценка токсичности текста отзыва')
    )

    moderator_comment = models.TextField(
        _('Комментарий модератора'), 
        blank=True,
        help_text=_('Комментарий оставленный модератором при обработке отзыва')
    )

    show_on_homepage = models.BooleanField(
        _('Показывать на главной'),
        default=False,
        db_index=True,
        help_text=_('Отметьте, чтобы отзыв попал в блок отзывов на главной странице.')
    )
    homepage_author_name = models.CharField(
        _('Имя для главной'),
        max_length=150,
        blank=True,
        help_text=_('Если пусто, будет использовано имя пользователя.')
    )
    homepage_main_photo = models.ImageField(
        _('Главное фото для главной'),
        upload_to='reviews/homepage/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Опциональное главное фото отзыва для блока на главной.')
    )
    homepage_order = models.PositiveIntegerField(
        _('Порядок на главной'),
        default=100,
        db_index=True,
        help_text=_('Меньше число - выше в списке.')
    )

    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True,
        help_text=_('Дата и время создания отзыва')
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True,
        help_text=_('Дата и время последнего обновления отзыва')
    )

    def can_be_edited(self):
        return self.status == ReviewStatus.PENDING

    @property
    def author_name(self):
        if self.is_admin_added:
            return f'{self.manual_last_name} {self.manual_first_name}'.strip()
        return self.user.get_full_name() or self.user.email

    def clean(self):
        super().clean()
        if self.is_admin_added:
            if self.user_id or not self.manual_first_name.strip() or not self.manual_last_name.strip():
                raise ValidationError(_('Для ручного отзыва нужны имя и фамилия, без аккаунта пользователя.'))
        elif not self.user_id or self.manual_first_name or self.manual_last_name:
            raise ValidationError(_('Отзыв сайта должен принадлежать пользователю, без ручного имени.'))

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = [['user', 'excursion']]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(is_admin_added=True, user__isnull=True) &
                    ~Q(manual_first_name='') & ~Q(manual_last_name='')
                ) | (
                    Q(is_admin_added=False, user__isnull=False) &
                    Q(manual_first_name='', manual_last_name='')
                ),
                name='review_author_matches_origin',
            ),
        ]

    def __str__(self):
        return f"Отзыв от {self.author_name} на {self.excursion.title} ({self.rating}★)"


class ReviewImage(models.Model):
    """Модель изображений к отзывам"""
    
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name=_('Отзыв'),
        help_text=_('Отзыв, к которому относится изображение')
    )
    image = models.ImageField(
        _('Фото'), 
        upload_to='reviews/%Y/%m/%d/',
        help_text=_('Фотография к отзыву')
    )
    is_homepage_main = models.BooleanField(
        _('Главное фото для главной'),
        default=False,
        db_index=True,
        help_text=_('Если отзыв показывается на главной, это фото будет первым.')
    )
    homepage_order = models.PositiveIntegerField(
        _('Порядок фото на главной'),
        default=100,
        db_index=True,
        help_text=_('Меньшее число - выше в фотоблоке отзыва на главной.')
    )
    uploaded_at = models.DateTimeField(
        _('Дата загрузки'),
        auto_now_add=True,
        help_text=_('Дата и время загрузки изображения')
    )

    class Meta:
        verbose_name = _('Фото к отзыву')
        verbose_name_plural = _('Фото к отзывам')
        ordering = ['homepage_order', '-is_homepage_main', 'uploaded_at']
