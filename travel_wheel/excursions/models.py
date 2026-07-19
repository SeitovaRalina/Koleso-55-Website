from django.db import models

class Category(models.Model):
    vk_id = models.IntegerField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )
    image = models.URLField(blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        full_path = [self.title]
        parent = self.parent
        while parent:
            full_path.insert(0, parent.title)
            parent = parent.parent
        return " → ".join(full_path)


class Excursion(models.Model):
    vk_id = models.BigIntegerField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration = models.PositiveIntegerField(help_text="Длительность в часах", null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='excursions',
        null=True,
        blank=True
    )
    main_image = models.URLField(blank=True)
    rating = models.FloatField(default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"

    def __str__(self):
        return self.title


class ExcursionImage(models.Model):
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name='images'
    )
    url = models.URLField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Изображение экскурсии"
        verbose_name_plural = "Изображения экскурсий"

    def __str__(self):
        return f"{self.excursion.title} - {self.url}"


class ExcursionSlot(models.Model):
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name='slots'
    )
    date = models.DateField()
    total_places = models.PositiveIntegerField()
    booked_places = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('excursion', 'date')
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"

    @property
    def available_places(self):
        return self.total_places - self.booked_places

    def __str__(self):
        return f"{self.excursion.title} - {self.date}"