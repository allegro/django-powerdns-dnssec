# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.models.powerdns
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0015_auto_20151214_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(unique=True, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], max_length=255, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='record',
            name='name',
            field=models.CharField(help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!", validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], default='fixme', max_length=255, verbose_name='name'),
            preserve_default=False,
        ),
    ]
