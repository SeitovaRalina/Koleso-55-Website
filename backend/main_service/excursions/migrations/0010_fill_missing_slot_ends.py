from datetime import datetime, timedelta

from django.db import migrations


def fill_missing_slot_ends(apps, schema_editor):
    Slot = apps.get_model('excursions', 'Slot')

    for slot in Slot.objects.select_related('excursion').filter(end_date__isnull=True, end_time__isnull=True):
        finish = datetime.combine(slot.date, slot.time) + timedelta(minutes=slot.excursion.duration)
        slot.end_date = finish.date()
        slot.end_time = finish.time()
        slot.save(update_fields=['end_date', 'end_time'])


class Migration(migrations.Migration):
    dependencies = [
        ('excursions', '0006_slot_end_and_excursion_labels'),
    ]

    operations = [
        migrations.RunPython(fill_missing_slot_ends, migrations.RunPython.noop),
    ]
