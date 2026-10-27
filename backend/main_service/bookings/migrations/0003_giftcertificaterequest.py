from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('bookings', '0002_tourorder_middle_name_alter_tourorder_comment_and_more')]

    operations = [
        migrations.CreateModel(
            name='GiftCertificateRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(max_length=150)),
                ('buyer_phone', models.CharField(max_length=30)),
                ('buyer_email', models.EmailField(max_length=254)),
                ('recipient_name', models.CharField(max_length=150)),
                ('recipient_phone', models.CharField(blank=True, max_length=30)),
                ('recipient_email', models.EmailField(blank=True, max_length=254)),
                ('amount', models.PositiveIntegerField()),
                ('format', models.CharField(choices=[('digital', 'Электронный'), ('printed', 'Печатный')], max_length=10)),
                ('message', models.TextField(blank=True, max_length=1000)),
                ('status', models.CharField(choices=[('new', 'Новая'), ('in_progress', 'В работе'), ('completed', 'Обработана'), ('cancelled', 'Отменена')], default='new', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Заявка на подарочный сертификат',
                'verbose_name_plural': 'Заявки на подарочные сертификаты',
                'ordering': ['-created_at'],
            },
        ),
    ]
