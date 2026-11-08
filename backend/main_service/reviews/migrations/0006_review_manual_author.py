from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0005_reviewimage_homepage_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='is_admin_added',
            field=models.BooleanField(default=False, editable=False, verbose_name='Добавлен администратором'),
        ),
        migrations.AddField(
            model_name='review',
            name='manual_first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Имя автора'),
        ),
        migrations.AddField(
            model_name='review',
            name='manual_last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Фамилия автора'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(
                blank=True,
                help_text='Автор отзыва',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reviews',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пользователь',
            ),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.CheckConstraint(
                condition=(
                    Q(is_admin_added=True, user__isnull=True) &
                    ~Q(manual_first_name='') & ~Q(manual_last_name='')
                ) | (
                    Q(is_admin_added=False, user__isnull=False) &
                    Q(manual_first_name='', manual_last_name='')
                ),
                name='review_author_matches_origin',
            ),
        ),
    ]
