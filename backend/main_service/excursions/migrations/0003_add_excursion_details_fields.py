# Generated migration manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excursions', '0002_alter_category_description_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='excursion',
            name='tour_format',
            field=models.CharField(
                choices=[('walking', 'Пешеходная'), ('bus', 'Автобусная'), ('water', 'Водная'), ('combined', 'Комбинированная')],
                default='walking',
                help_text='Формат проведения экскурсии',
                max_length=20,
                verbose_name='Формат поездки'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='group_size',
            field=models.PositiveIntegerField(
                default=20,
                help_text='Максимальное количество человек в группе',
                verbose_name='Размер группы'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='is_multi_day',
            field=models.BooleanField(
                default=False,
                help_text='Является ли экскурсия многодневным туром',
                verbose_name='Многодневный тур'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='included_in_price',
            field=models.TextField(
                blank=True,
                help_text='Перечень услуг, включенных в стоимость',
                verbose_name='Что входит в стоимость'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='not_included_in_price',
            field=models.TextField(
                blank=True,
                help_text='Перечень услуг, не включенных в стоимость',
                verbose_name='Что не входит в стоимость'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='what_to_bring',
            field=models.TextField(
                blank=True,
                help_text='Рекомендации по вещам и экипировке',
                verbose_name='Что взять с собой'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='meeting_point',
            field=models.CharField(
                blank=True,
                help_text='Место сбора группы',
                max_length=500,
                verbose_name='Место встречи'
            ),
        ),
        migrations.AddField(
            model_name='excursion',
            name='departure_time',
            field=models.TimeField(
                blank=True,
                help_text='Время начала экскурсии',
                null=True,
                verbose_name='Время отправления'
            ),
        ),
    ]
