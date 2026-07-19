from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from excursions.models import Excursion


class ExcursionView(models.Model):
    class SourceChoices(models.TextChoices):
        SEARCH = 'search', _('Поиск')
        CATALOG = 'catalog', _('Каталог')
        RECOMMENDATION = 'recommendation', _('Рекомендации')
        SIMILAR = 'similar', _('Похожие экскурсии')
        DIRECT = 'direct', _('Прямой переход')

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='excursion_views',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, просмотревший экскурсию')
    )
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_('Экскурсия'),
        help_text=_('Просмотренная экскурсия')
    )
    session_id = models.CharField(
        _('ID сессии'),
        max_length=255,
        db_index=True,
        help_text=_('Идентификатор сессии для анонимных пользователей')
    )
    duration_seconds = models.PositiveIntegerField(
        _('Длительность просмотра (сек)'),
        default=0,
        help_text=_('Общая длительность просмотра в секундах')
    )
    source = models.CharField(
        _('Источник перехода'),
        max_length=20,
        choices=SourceChoices.choices,
        default=SourceChoices.CATALOG,
        help_text=_('Откуда пользователь перешел на страницу экскурсии')
    )
    started_at = models.DateTimeField(
        _('Время начала'),
        auto_now_add=True,
        help_text=_('Время начала просмотра экскурсии')
    )
    processed_for_recommendations = models.BooleanField(
        _('Обработано для рекомендаций'),
        default=False,
        help_text=_('Были ли данные отправлены в систему рекомендаций')
    )

    class Meta:
        verbose_name = _('Просмотр экскурсии')
        verbose_name_plural = _('Просмотры экскурсий')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['excursion', 'started_at']),
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['session_id', 'started_at']),
        ]

    def __str__(self):
        user_info = f"Пользователь {self.user.email}" if self.user else f"Сессия {self.session_id}"
        return f"{user_info} - {self.excursion.title} ({self.started_at})"
