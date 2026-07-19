from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_reviewimage_options_alter_review_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='homepage_author_name',
            field=models.CharField(
                blank=True,
                help_text='Если пусто, будет использовано имя пользователя.',
                max_length=150,
                verbose_name='Имя для главной',
            ),
        ),
        migrations.AddField(
            model_name='review',
            name='homepage_main_photo',
            field=models.ImageField(
                blank=True,
                help_text='Опциональное главное фото отзыва для блока на главной.',
                null=True,
                upload_to='reviews/homepage/%Y/%m/%d/',
                verbose_name='Главное фото для главной',
            ),
        ),
        migrations.AddField(
            model_name='review',
            name='homepage_order',
            field=models.PositiveIntegerField(
                db_index=True,
                default=100,
                help_text='Меньше число - выше в списке.',
                verbose_name='Порядок на главной',
            ),
        ),
        migrations.AddField(
            model_name='review',
            name='show_on_homepage',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='Отметьте, чтобы отзыв попал в блок отзывов на главной странице.',
                verbose_name='Показывать на главной',
            ),
        ),
    ]
