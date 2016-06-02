# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0022_auto_20160531_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='domaintemplate',
            name='is_public_domain',
            field=models.BooleanField(default=False),
        ),
    ]
