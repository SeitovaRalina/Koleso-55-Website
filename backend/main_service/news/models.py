from django.db import models
from django.utils import timezone


class NewsArticle(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Адрес', max_length=220, unique=True, allow_unicode=True)
    excerpt = models.TextField('Анонс', max_length=500)
    body = models.TextField('Текст')
    cover = models.ImageField('Обложка', upload_to='news/', blank=True)
    category = models.CharField('Категория', max_length=80, blank=True)
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    is_published = models.BooleanField('Опубликовано', default=False, db_index=True)

    class Meta:
        ordering = ['-published_at', '-pk']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title
