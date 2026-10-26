from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('slug', models.SlugField(allow_unicode=True, max_length=220, unique=True, verbose_name='Адрес')),
                ('excerpt', models.TextField(max_length=500, verbose_name='Анонс')),
                ('body', models.TextField(verbose_name='Текст')),
                ('cover', models.ImageField(blank=True, upload_to='news/', verbose_name='Обложка')),
                ('category', models.CharField(blank=True, max_length=80, verbose_name='Категория')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата публикации')),
                ('is_published', models.BooleanField(db_index=True, default=False, verbose_name='Опубликовано')),
            ],
            options={'verbose_name': 'Новость', 'verbose_name_plural': 'Новости', 'ordering': ['-published_at', '-pk']},
        ),
    ]
