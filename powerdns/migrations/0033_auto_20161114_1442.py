# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0032_auto_20161102_2006'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='domainowner',
            unique_together=set([('domain', 'owner', 'ownership_type')]),
        ),
    ]
