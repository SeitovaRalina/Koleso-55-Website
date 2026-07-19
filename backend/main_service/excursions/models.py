from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Модель категорий экскурсий"""
    
    name = models.CharField(
        'Название', 
        max_length=100, 
        unique=True,
        help_text='Название категории экскурсий'
    )
    slug = models.SlugField(
        'Slug', 
        max_length=120, 
        unique=True, 
        blank=True,
        help_text='URL-совместимое название категории'
    )
    description = models.TextField(
        'Описание', 
        blank=True,
        help_text='Подробное описание категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Excursion(models.Model):
    class LocationType(models.TextChoices):
        CITY = 'city', 'Городские экскурсии'
        SUBURBAN = 'suburban', 'Загородные экскурсии'
        RUSSIA = 'russia', 'Туры по России'

    class TourFormat(models.TextChoices):
        WALKING = 'walking', 'Пешеходная'
        BUS = 'bus', 'Автобусная'
        WATER = 'water', 'Водная'
        COMBINED = 'combined', 'Комбинированная'

    title = models.CharField(
        'Название экскурсии', 
        max_length=200,
        help_text='Название экскурсии'
    )
    slug = models.SlugField(
        'Slug', 
        max_length=250, 
        unique=True, 
        blank=True,
        help_text='URL-совместимое название экскурсии'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='excursions',
        verbose_name='Категория',
        help_text='Категория, к которой относится экскурсия'
    )
    location_type = models.CharField(
        'Тип локации',
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.CITY,
        db_index=True,
        help_text='Тип местоположения проведения экскурсии'
    )
    tour_format = models.CharField(
        'Формат поездки',
        max_length=20,
        choices=TourFormat.choices,
        default=TourFormat.WALKING,
        help_text='Формат проведения экскурсии'
    )
    group_size = models.PositiveIntegerField(
        'Размер группы',
        default=20,
        help_text='Максимальное количество человек в группе'
    )
    is_multi_day = models.BooleanField(
        'Многодневный тур',
        default=False,
        help_text='Является ли экскурсия многодневным туром'
    )
    description = models.TextField(
        'Полное описание',
        help_text='Подробное описание экскурсии'
    )
    short_description = models.TextField(
        'Краткое описание', 
        max_length=500,
        help_text='Краткое описание экскурсии для превью'
    )
    included_in_price = models.TextField(
        'Что входит в стоимость',
        blank=True,
        help_text='Перечень услуг, включенных в стоимость'
    )
    not_included_in_price = models.TextField(
        'Что не входит в стоимость',
        blank=True,
        help_text='Перечень услуг, не включенных в стоимость'
    )
    what_to_bring = models.TextField(
        'Что взять с собой',
        blank=True,
        help_text='Рекомендации по вещам и экипировке'
    )
    meeting_point = models.CharField(
        'Место встречи',
        max_length=500,
        blank=True,
        help_text='Место сбора группы'
    )
    departure_time = models.TimeField(
        'Время отправления',
        null=True,
        blank=True,
        help_text='Время начала экскурсии'
    )
    price = models.DecimalField(
        'Цена от (руб)', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Минимальная цена участия в экскурсии'
    )
    duration = models.PositiveIntegerField(
        _('Длительность (мин)'), 
        help_text=_('Продолжительность экскурсии в минутах')
    )
    is_active = models.BooleanField(
        _('Активна'), 
        default=True,
        help_text=_('Доступна ли экскурсия для бронирования')
    )
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True,
        help_text=_('Дата и время создания экскурсии')
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True,
        help_text=_('Дата и время последнего обновления экскурсии')
    )

    class Meta:
        verbose_name = _('Экскурсия')
        verbose_name_plural = _('Экскурсии')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ExcursionImage(models.Model):
    """Модель изображений экскурсий"""
    
    excursion = models.ForeignKey(
        Excursion, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Экскурсия',
        help_text='Экскурсия, к которой относится изображение'
    )
    image = models.ImageField(
        'Фото', 
        upload_to='excursions/%Y/%m/%d/',
        help_text='Фотография экскурсии'
    )
    alt_text = models.CharField(
        'Alt-текст', 
        max_length=200, 
        blank=True,
        help_text='Альтернативный текст для изображения'
    )
    is_main = models.BooleanField(
        'Главное фото', 
        default=False,
        help_text='Является ли изображение главным для экскурсии'
    )

    class Meta:
        verbose_name = 'Фото экскурсии'
        verbose_name_plural = 'Фото экскурсий'
        ordering = ['-is_main', 'id']

    def __str__(self):
        return f'Фото для {self.excursion.title}'


class Slot(models.Model):
    """Модель временных слотов для проведения экскурсий"""
    
    excursion = models.ForeignKey(
        Excursion, 
        on_delete=models.CASCADE, 
        related_name='slots',
        verbose_name='Экскурсия',
        help_text='Экскурсия, для которой создан слот'
    )
    date = models.DateField(
        'Дата',
        help_text='Дата проведения экскурсии'
    )
    time = models.TimeField(
        'Время начала',
        help_text='Время начала проведения экскурсии'
    )
    max_participants = models.PositiveIntegerField(
        'Макс. человек', 
        default=20,
        help_text='Максимальное количество участников'
    )
    booked_participants = models.PositiveIntegerField(
        'Забронировано', 
        default=0,
        help_text='Количество забронированных мест'
    )
    price_override = models.DecimalField(
        'Цена для этого слота (если отличается)', 
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text='Особая цена для этого слота, если отличается от базовой'
    )

    class Meta:
        verbose_name = 'Слот'
        verbose_name_plural = 'Слоты'
        unique_together = [['excursion', 'date', 'time']]
        ordering = ['date', 'time']

    def __str__(self):
        return f'{self.excursion.title} — {self.date} {self.time}'

    @property
    def available_seats(self):
        return self.max_participants - self.booked_participants

    @property
    def is_available(self):
        return self.available_seats > 0 and self.excursion.is_active


class ExcursionProgramDay(models.Model):
    """Модель программы по дням для многодневных туров"""
    
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name='program_days',
        verbose_name='Экскурсия',
        help_text='Экскурсия, к которой относится день программы'
    )
    day_number = models.PositiveIntegerField(
        'Номер дня',
        help_text='Порядковый номер дня в туре'
    )
    title = models.CharField(
        'Заголовок дня',
        max_length=200,
        help_text='Название или тема дня'
    )
    description = models.TextField(
        'Описание программы дня',
        help_text='Подробное описание программы на этот день'
    )

    class Meta:
        verbose_name = 'День программы'
        verbose_name_plural = 'Дни программы'
        unique_together = [['excursion', 'day_number']]
        ordering = ['day_number']

    def __str__(self):
        return f'День {self.day_number}: {self.title}'


class TicketType(models.Model):
    """Модель типов билетов (взрослый/детский и т.д.)"""
    
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name='ticket_types',
        verbose_name='Экскурсия',
        help_text='Экскурсия, к которой относится тип билета'
    )
    name = models.CharField(
        'Название типа',
        max_length=50,
        help_text='Например: Взрослый, Детский, Студенческий'
    )
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Цена билета данного типа'
    )
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Доступен ли данный тип билета для бронирования'
    )

    class Meta:
        verbose_name = 'Тип билета'
        verbose_name_plural = 'Типы билетов'
        unique_together = [['excursion', 'name']]
        ordering = ['id']

    def __str__(self):
        return f'{self.name} - {self.price} ₽'
