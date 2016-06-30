# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0023_domaintemplate_is_public_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='deleterequest',
            name='last_change_json',
            field=django_extensions.db.fields.json.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='last_change_json',
            field=django_extensions.db.fields.json.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='last_change_json',
            field=django_extensions.db.fields.json.JSONField(null=True, blank=True),
        ),
    ]
