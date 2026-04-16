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
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews'
    )
    excursion = models.ForeignKey(
        Excursion, on_delete=models.CASCADE, related_name='reviews'
    )
    order = models.ForeignKey(
        TourOrder, on_delete=models.SET_NULL, null=True, blank=True
    )

    rating = models.PositiveSmallIntegerField(
        'Оценка', choices=[(i, str(i)) for i in range(1, 6)]
    )
    text = models.TextField('Отзыв', max_length=2000)

    status = models.CharField(
        'Статус модерации',
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING
    )
    is_toxic = models.BooleanField('Содержит нецензурную лексику', default=False)
    toxicity_score = models.FloatField('Степень токсичности', default=0.0)

    moderator_comment = models.TextField('Комментарий модератора', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = [['user', 'excursion']]

    def __str__(self):
        return f"Отзыв от {self.user.get_full_name()} на {self.excursion.title} ({self.rating}★)"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Фото', upload_to='reviews/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фото к отзыву'
        verbose_name_plural = 'Фото к отзывам'
