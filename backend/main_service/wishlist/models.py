from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from excursions.models import Excursion


class Wishlist(models.Model):
    """Модель избранного для хранения экскурсий, добавленных пользователями в избранное"""
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, добавивший экскурсию в избранное')
    )
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name='wishlist_entries',
        verbose_name=_('Экскурсия'),
        help_text=_('Экскурсия, добавленная в избранное')
    )
    added_at = models.DateTimeField(
        _('Дата добавления'),
        auto_now_add=True,
        help_text=_('Дата и время добавления экскурсии в избранное')
    )

    class Meta:
        verbose_name = _('Избранная экскурсия')
        verbose_name_plural = _('Избранные экскурсии')
        unique_together = ['user', 'excursion']
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', '-added_at']),
            models.Index(fields=['excursion']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.excursion.title}"
