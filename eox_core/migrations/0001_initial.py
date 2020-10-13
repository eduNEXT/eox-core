# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-15 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, help_text=u'use only the domain name, e.g. cursos.edunext.co', max_length=253)),
                ('target', models.CharField(max_length=253)),
                ('scheme', models.CharField(choices=[(u'http', u'http'), (u'https', u'https')], default=u'http', max_length=5)),
                ('status', models.IntegerField(choices=[(301, u'Temporary'), (302, u'Permanent')], default=301)),
            ],
            options={
                'db_table': 'edunext_redirection',
            },
        ),
    ]
