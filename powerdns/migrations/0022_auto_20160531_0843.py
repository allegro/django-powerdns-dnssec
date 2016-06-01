# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0021_tsigkey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(help_text='The record for which a change is being requested', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='powerdns.Record', related_name='requests', db_constraint=False, null=True),
        ),
    ]
