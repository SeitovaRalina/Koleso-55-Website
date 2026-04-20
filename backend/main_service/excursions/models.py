from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=120, unique=True, blank=True)
    description = models.TextField('Описание', blank=True)

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

    title = models.CharField('Название экскурсии', max_length=200)
    slug = models.SlugField('Slug', max_length=250, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='excursions',
        verbose_name='Категория'
    )
    location_type = models.CharField(
        'Тип локации',
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.CITY,
        db_index=True
    )
    description = models.TextField('Полное описание')
    short_description = models.TextField('Краткое описание', max_length=500)
    price = models.DecimalField(
        'Цена от (руб)', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duration = models.PositiveIntegerField('Длительность (мин)')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Экскурсия'
        verbose_name_plural = 'Экскурсии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ExcursionImage(models.Model):
    excursion = models.ForeignKey(
        Excursion, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField('Фото', upload_to='excursions/%Y/%m/%d/')
    alt_text = models.CharField('Alt-текст', max_length=200, blank=True)
    is_main = models.BooleanField('Главное фото', default=False)

    class Meta:
        verbose_name = 'Фото экскурсии'
        verbose_name_plural = 'Фото экскурсий'
        ordering = ['-is_main', 'id']

    def __str__(self):
        return f'Фото для {self.excursion.title}'


class Slot(models.Model):
    excursion = models.ForeignKey(
        Excursion, on_delete=models.CASCADE, related_name='slots'
    )
    date = models.DateField('Дата')
    time = models.TimeField('Время начала')
    max_participants = models.PositiveIntegerField('Макс. человек', default=20)
    booked_participants = models.PositiveIntegerField('Забронировано', default=0)
    price_override = models.DecimalField(
        'Цена для этого слота (если отличается)', max_digits=10, decimal_places=2,
        null=True, blank=True
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
