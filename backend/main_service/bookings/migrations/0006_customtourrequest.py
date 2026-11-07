from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookings', '0005_alter_giftcertificaterequest_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomTourRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Имя')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Электронная почта')),
                ('description', models.TextField(max_length=2000, verbose_name='Пожелания')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('in_progress', 'В работе'), ('completed', 'Обработана'), ('cancelled', 'Отменена')], default='new', max_length=20, verbose_name='Статус обработки')),
                ('manager_comment', models.TextField(blank=True, verbose_name='Комментарий менеджера')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_tour_requests', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={'verbose_name': 'Заявка на экскурсию на заказ', 'verbose_name_plural': 'Заявки на экскурсии на заказ', 'ordering': ['-created_at']},
        ),
    ]
