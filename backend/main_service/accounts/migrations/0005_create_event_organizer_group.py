from django.db import migrations


ORGANIZER_GROUP = 'Организатор мероприятий'
EXCURSION_MODELS = ('category', 'excursion', 'excursionimage', 'excursionprogramday', 'slot', 'tickettype')


def create_organizer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, _ = Group.objects.get_or_create(name=ORGANIZER_GROUP)
    codenames = [
        f'{action}_{model}'
        for action in ('add', 'change', 'delete', 'view')
        for model in EXCURSION_MODELS
    ]
    permissions = Permission.objects.filter(
        content_type__app_label='excursions',
        content_type__model__in=EXCURSION_MODELS,
        codename__in=codenames,
    )
    group.permissions.set(permissions)


def remove_organizer_group(apps, schema_editor):
    apps.get_model('auth', 'Group').objects.filter(name=ORGANIZER_GROUP).delete()


class Migration(migrations.Migration):
    dependencies = [('accounts', '0004_customuser_email_verification_sent_at')]

    operations = [migrations.RunPython(create_organizer_group, remove_organizer_group)]
