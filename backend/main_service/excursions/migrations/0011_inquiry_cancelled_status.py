from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('excursions', '0009_inquiry_email_contact'),
        ('excursions', '0010_fill_missing_slot_ends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='excursioninquiry',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'Новое'),
                    ('in_progress', 'В работе'),
                    ('closed', 'Вопрос решён'),
                    ('cancelled', 'Отменено'),
                ],
                default='new',
                max_length=20,
                verbose_name='Статус обработки',
            ),
        ),
    ]
