# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0033_auto_20161114_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='require_sec_acceptance',
            field=models.BooleanField(help_text='Do new A records require security acceptance', default=False),
        ),
        migrations.AddField(
            model_name='domain',
            name='require_seo_acceptance',
            field=models.BooleanField(help_text='Does deleting A records require SEO acceptance', default=False),
        ),
    ]
