from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('excursions', '0006_excursioninquiry'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='excursioninquiry',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='excursioninquiry',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='excursion_inquiries', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
