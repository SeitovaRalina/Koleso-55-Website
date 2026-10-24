from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('excursions', '0005_alter_excursionprogramday_excursion_and_more')]

    operations = [
        migrations.AddField(model_name='slot', name='end_date', field=models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
        migrations.AddField(model_name='slot', name='end_time', field=models.TimeField(blank=True, null=True, verbose_name='Время окончания')),
        migrations.AlterField(model_name='excursion', name='title', field=models.CharField(help_text='Название экскурсии', max_length=200, verbose_name='Название программы или экскурсии')),
        migrations.AlterModelOptions(name='excursion', options={'ordering': ['-created_at'], 'verbose_name': 'Программа или экскурсия', 'verbose_name_plural': 'Программы и экскурсии'}),
    ]
