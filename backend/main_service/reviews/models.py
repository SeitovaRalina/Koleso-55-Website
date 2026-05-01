from django.db import models
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
        verbose_name=_('Пользователь'),
        help_text=_('Автор отзыва')
    )
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

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = [['user', 'excursion']]

    def __str__(self):
        return f"Отзыв от {self.user.get_full_name()} на {self.excursion.title} ({self.rating}★)"


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
    uploaded_at = models.DateTimeField(
        _('Дата загрузки'),
        auto_now_add=True,
        help_text=_('Дата и время загрузки изображения')
    )

    class Meta:
        verbose_name = _('Фото к отзыву')
        verbose_name_plural = _('Фото к отзывам')
        ordering = ['-uploaded_at']
