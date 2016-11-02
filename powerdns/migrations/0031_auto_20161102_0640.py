# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0030_auto_20161026_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='domainrequest',
            name='target_service',
            field=models.ForeignKey(blank=True, null=True, to='powerdns.Service'),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='target_service',
            field=models.ForeignKey(blank=True, null=True, to='powerdns.Service'),
        ),
    ]
