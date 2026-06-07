from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_homepage_review_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewimage',
            name='homepage_order',
            field=models.PositiveIntegerField(
                db_index=True,
                default=100,
                help_text='Меньшее число - выше в фотоблоке отзыва на главной.',
                verbose_name='Порядок фото на главной',
            ),
        ),
        migrations.AddField(
            model_name='reviewimage',
            name='is_homepage_main',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='Если отзыв показывается на главной, это фото будет первым.',
                verbose_name='Главное фото для главной',
            ),
        ),
        migrations.AlterModelOptions(
            name='reviewimage',
            options={
                'ordering': ['homepage_order', '-is_homepage_main', 'uploaded_at'],
                'verbose_name': 'Фото к отзыву',
                'verbose_name_plural': 'Фото к отзывам',
            },
        ),
    ]
