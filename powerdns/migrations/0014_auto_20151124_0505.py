# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import powerdns.models.powerdns


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0013_auto_20151124_0301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], verbose_name='name', unique=True),
        ),
    ]
