# Generated migration manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excursions', '0003_add_excursion_details_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcursionProgramDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.PositiveIntegerField(help_text='Порядковый номер дня в туре', verbose_name='Номер дня')),
                ('title', models.CharField(help_text='Название или тема дня', max_length=200, verbose_name='Заголовок дня')),
                ('description', models.TextField(help_text='Подробное описание программы на этот день', verbose_name='Описание программы дня')),
                ('excursion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_days', to='excursions.excursion', verbose_name='Экскурсия')),
            ],
            options={
                'verbose_name': 'День программы',
                'verbose_name_plural': 'Дни программы',
                'ordering': ['day_number'],
            },
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Например: Взрослый, Детский, Студенческий', max_length=50, verbose_name='Название типа')),
                ('price', models.DecimalField(decimal_places=2, help_text='Цена билета данного типа', max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена')),
                ('is_active', models.BooleanField(default=True, help_text='Доступен ли данный тип билета для бронирования', verbose_name='Активен')),
                ('excursion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_types', to='excursions.excursion', verbose_name='Экскурсия')),
            ],
            options={
                'verbose_name': 'Тип билета',
                'verbose_name_plural': 'Типы билетов',
                'ordering': ['id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='excursionprogramday',
            unique_together={('excursion', 'day_number')},
        ),
        migrations.AlterUniqueTogether(
            name='tickettype',
            unique_together={('excursion', 'name')},
        ),
    ]
