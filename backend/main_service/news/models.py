from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class NewsCategory(models.Model):
    name = models.CharField('Название', max_length=80)
    slug = models.SlugField('Адрес', max_length=100, unique=True, allow_unicode=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория новостей'
        verbose_name_plural = 'Категории новостей'

    def __str__(self):
        return self.name


class NewsArticle(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Адрес', max_length=220, unique=True, allow_unicode=True)
    excerpt = models.TextField('Анонс', max_length=500)
    body = models.TextField('Прежний текст', blank=True, help_text='Сохранён для старых материалов; новый материал собирается из блоков.')
    cover = models.ImageField('Обложка', upload_to='news/', blank=True)
    category = models.ForeignKey(NewsCategory, verbose_name='Категория', on_delete=models.PROTECT, null=True, blank=True, related_name='articles')
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    is_published = models.BooleanField('Опубликовано', default=False, db_index=True)

    class Meta:
        ordering = ['-published_at', '-pk']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title


class NewsBlock(models.Model):
    class Kind(models.TextChoices):
        HEADING = 'heading', 'Подзаголовок'
        PARAGRAPH = 'paragraph', 'Абзац'
        IMAGE = 'image', 'Изображение'

    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='blocks', verbose_name='Новость')
    position = models.PositiveIntegerField('Порядок', default=0)
    kind = models.CharField('Тип блока', max_length=12, choices=Kind.choices)
    text = models.TextField('Текст', blank=True)
    image = models.ImageField('Изображение', upload_to='news/blocks/', blank=True)
    alt = models.CharField('Описание изображения', max_length=200, blank=True)
    caption = models.CharField('Подпись', max_length=300, blank=True)

    class Meta:
        ordering = ['position', 'pk']
        verbose_name = 'Блок новости'
        verbose_name_plural = 'Блоки новости'

    def clean(self):
        errors = {}
        if self.kind == self.Kind.IMAGE:
            if not self.image:
                errors['image'] = 'Загрузите изображение.'
            if not self.alt.strip():
                errors['alt'] = 'Добавьте описание изображения.'
            if self.text.strip():
                errors['text'] = 'Текст доступен только для подзаголовка и абзаца.'
        elif self.kind in (self.Kind.HEADING, self.Kind.PARAGRAPH):
            if not self.text.strip():
                errors['text'] = 'Введите текст.'
            if self.image:
                errors['image'] = 'Изображение доступно только для блока изображения.'
            if self.alt.strip() or self.caption.strip():
                errors['alt'] = 'Описание и подпись доступны только для изображения.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.get_kind_display()} #{self.position}'
