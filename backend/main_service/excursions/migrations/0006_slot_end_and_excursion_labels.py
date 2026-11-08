from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('excursions', '0005_alter_excursionprogramday_excursion_and_more')]

    operations = [
        migrations.AddField(model_name='slot', name='end_date', field=models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
        migrations.AddField(model_name='slot', name='end_time', field=models.TimeField(blank=True, null=True, verbose_name='Время окончания')),
        migrations.AlterField(model_name='excursion', name='title', field=models.CharField(help_text='Название программы, экскурсии или встречи', max_length=200, verbose_name='Название программы или экскурсии')),
        migrations.AlterField(model_name='excursion', name='category', field=models.ForeignKey(help_text='Категория программы или экскурсии', on_delete=models.deletion.PROTECT, related_name='excursions', to='excursions.category', verbose_name='Категория')),
        migrations.AlterField(model_name='excursion', name='is_multi_day', field=models.BooleanField(default=False, help_text='Программа проходит в несколько календарных дней', verbose_name='Многодневная программа')),
        migrations.AlterField(model_name='slot', name='excursion', field=models.ForeignKey(help_text='Программа или экскурсия, для которой создан слот', on_delete=models.deletion.CASCADE, related_name='slots', to='excursions.excursion', verbose_name='Программа или экскурсия')),
        migrations.AlterModelOptions(name='excursion', options={'ordering': ['-created_at'], 'verbose_name': 'Программа или экскурсия', 'verbose_name_plural': 'Программы и экскурсии'}),
    ]
