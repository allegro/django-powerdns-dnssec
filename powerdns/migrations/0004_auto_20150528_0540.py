# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0003_auto_20150527_0808'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='remarks',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='record',
            name='remarks',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
