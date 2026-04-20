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
        verbose_name='Пользователь'
    )
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Экскурсия'
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Слот'
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    phone = models.CharField('Телефон', max_length=20)
    contact_method = models.CharField(
        'Предпочитаемый способ связи',
        max_length=20,
        choices=ContactMethod.choices,
        default=ContactMethod.CALL
    )
    email = models.EmailField('Email', blank=True, help_text='Укажите email, если предпочитаете связь по почте')

    num_participants = models.PositiveIntegerField(
        'Количество человек',
        validators=[MinValueValidator(1)]
    )
    comment = models.TextField('Комментарий клиента', blank=True)

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW
    )

    manager_comment = models.TextField('Комментарий менеджера', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
