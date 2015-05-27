# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0002_auto_20150514_0638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='auth',
            field=models.NullBooleanField(help_text='Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records', verbose_name='authoritative', default=True),
        ),
    ]
