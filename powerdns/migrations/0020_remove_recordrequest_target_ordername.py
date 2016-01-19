# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0019_auto_20160111_0842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recordrequest',
            name='target_ordername',
        ),
    ]
