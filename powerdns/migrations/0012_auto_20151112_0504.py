# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.models.powerdns
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0011_auto_20151103_0546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(verbose_name='name', max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], unique=True),
        ),
    ]
