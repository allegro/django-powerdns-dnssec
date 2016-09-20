# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0027_auto_20160915_0349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='number',
            field=models.DecimalField(default=None, decimal_places=0, max_digits=39, db_index=True, blank=True, verbose_name='IP number', null=True, editable=False),
        ),
    ]
