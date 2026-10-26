from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def move_existing_content(apps, schema_editor):
    Article = apps.get_model('news', 'NewsArticle')
    Category = apps.get_model('news', 'NewsCategory')
    Block = apps.get_model('news', 'NewsBlock')
    categories = {}
    for article in Article.objects.all().iterator():
        old_category = article.legacy_category.strip()
        if old_category:
            if old_category not in categories:
                base = slugify(old_category, allow_unicode=True)[:90] or 'category'
                slug = base
                suffix = 2
                while Category.objects.filter(slug=slug).exists():
                    slug = f'{base[:90-len(str(suffix))]}-{suffix}'
                    suffix += 1
                categories[old_category] = Category.objects.create(name=old_category, slug=slug).pk
            article.category_id = categories[old_category]
            article.save(update_fields=['category'])
        if article.body.strip():
            Block.objects.create(article_id=article.pk, position=1, kind='paragraph', text=article.body)


class Migration(migrations.Migration):
    dependencies = [('news', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Название')),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='Адрес')),
            ],
            options={'ordering': ['name'], 'verbose_name': 'Категория новостей', 'verbose_name_plural': 'Категории новостей'},
        ),
        migrations.RenameField(model_name='newsarticle', old_name='category', new_name='legacy_category'),
        migrations.AlterField(model_name='newsarticle', name='body', field=models.TextField(blank=True, help_text='Сохранён для старых материалов; новый материал собирается из блоков.', verbose_name='Прежний текст')),
        migrations.AddField(
            model_name='newsarticle', name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='articles', to='news.newscategory', verbose_name='Категория'),
        ),
        migrations.CreateModel(
            name='NewsBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('kind', models.CharField(choices=[('heading', 'Подзаголовок'), ('paragraph', 'Абзац'), ('image', 'Изображение')], max_length=12, verbose_name='Тип блока')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
                ('image', models.ImageField(blank=True, upload_to='news/blocks/', verbose_name='Изображение')),
                ('alt', models.CharField(blank=True, max_length=200, verbose_name='Описание изображения')),
                ('caption', models.CharField(blank=True, max_length=300, verbose_name='Подпись')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='news.newsarticle', verbose_name='Новость')),
            ],
            options={'ordering': ['position', 'pk'], 'verbose_name': 'Блок новости', 'verbose_name_plural': 'Блоки новости'},
        ),
        migrations.RunPython(move_existing_content, migrations.RunPython.noop),
        migrations.RemoveField(model_name='newsarticle', name='legacy_category'),
    ]
