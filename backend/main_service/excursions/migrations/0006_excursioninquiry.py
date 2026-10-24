import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('excursions', '0005_alter_excursionprogramday_excursion_and_more')]

    operations = [
        migrations.CreateModel(
            name='ExcursionInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Ключ отправки')),
                ('name', models.CharField(max_length=120, verbose_name='Имя')),
                ('phone', models.CharField(max_length=18, verbose_name='Телефон')),
                ('contact_method', models.CharField(choices=[('call', 'Звонок'), ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('max', 'MAX')], max_length=20, verbose_name='Способ связи')),
                ('question', models.TextField(max_length=2000, verbose_name='Вопрос')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата обращения')),
                ('status', models.CharField(choices=[('new', 'Новое'), ('in_progress', 'В работе'), ('closed', 'Закрыто')], default='new', max_length=20, verbose_name='Статус обработки')),
                ('excursion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inquiries', to='excursions.excursion', verbose_name='Программа')),
            ],
            options={'verbose_name': 'Обращение по программе', 'verbose_name_plural': 'Обращения по программам', 'ordering': ['-created_at']},
        ),
    ]
