# -*- coding: utf-8 -*-
from django.db import migrations


def update_contentypes(apps, schema_editor):
    """
    Updates content types.
    We want to have the same content type id, when the model is moved.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias
    # Move the Redirection to eox_core
    qs = ContentType.objects.using(db_alias).filter(app_label='eox_tenant', model='Redirection')
    qs.update(app_label='eox_core')


def update_contentypes_reverse(apps, schema_editor):
    """
    Reverts changes in content types.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias
    qs = ContentType.objects.using(db_alias).filter(app_label='eox_core', model='Redirection')
    qs.update(app_label='eox_tenant')


class Migration(migrations.Migration):
    dependencies = [
        ('eox_core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_contentypes, update_contentypes_reverse)
    ]
