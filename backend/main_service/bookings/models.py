from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from accounts.models import CustomUser
from excursions.models import Excursion, Slot

class ContactMethod(models.TextChoices):
    CALL = 'call', 'Звонок'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    TELEGRAM = 'telegram', 'Telegram'
    MAX = 'max', 'Max'
    EMAIL = 'email', 'Email'

class OrderStatus(models.TextChoices):
    NEW = 'new', _('Новый')
    CONFIRMED = 'confirmed', _('Подтверждён')
    PAID = 'paid', _('Оплачен')
    CANCELLED = 'cancelled', _('Отменён')
    COMPLETED = 'completed', _('Выполнен')


class TourOrder(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, сделавший заказ')
    )
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('Экскурсия'),
        help_text=_('Экскурсия, на которую оформлен заказ')
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('Слот'),
        help_text=_('Временной слот для проведения экскурсии')
    )
    first_name = models.CharField(
        _('Имя'), 
        max_length=150,
        help_text=_('Имя клиента')
    )
    last_name = models.CharField(
        _('Фамилия'), 
        max_length=150, 
        blank=True,
        help_text=_('Фамилия клиента')
    )
    phone = models.CharField(
        _('Телефон'), 
        max_length=20,
        help_text=_('Контактный номер телефона клиента')
    )
    contact_method = models.CharField(
        _('Предпочитаемый способ связи'),
        max_length=20,
        choices=ContactMethod.choices,
        default=ContactMethod.CALL,
        help_text=_('Как с вами связаться для подтверждения заказа')
    )
    email = models.EmailField(
        _('Email'), 
        blank=True, 
        help_text=_('Укажите email, если предпочитаете связь по почте')
    )

    num_participants = models.PositiveIntegerField(
        _('Количество человек'),
        validators=[MinValueValidator(1)],
        help_text=_('Количество участников экскурсии')
    )
    comment = models.TextField(
        _('Комментарий клиента'), 
        blank=True,
        help_text=_('Дополнительная информация от клиента')
    )

    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        help_text=_('Текущий статус заказа')
    )

    manager_comment = models.TextField(
        _('Комментарий менеджера'), 
        blank=True,
        help_text=_('Внутренний комментарий для менеджеров')
    )

    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True,
        help_text=_('Дата и время создания заказа')
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True,
        help_text=_('Дата и время последнего обновления заказа')
    )

    class Meta:
        verbose_name = 'Заказ на экскурсию'
        verbose_name_plural = 'Заказы на экскурсии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} — {self.excursion.title} ({self.status})'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if self.pk:
            old_order = TourOrder.objects.get(pk=self.pk)
            if self.status == OrderStatus.PAID and old_order.status != OrderStatus.PAID:
                self.slot.booked_participants += self.num_participants
                self.slot.save()
            elif self.status == OrderStatus.CANCELLED:
                self.slot.booked_participants = max(0, self.slot.booked_participants - self.num_participants)
                self.slot.save()

        super().save(*args, **kwargs)
