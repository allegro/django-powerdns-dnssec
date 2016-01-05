# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import powerdns.models.powerdns


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0016_auto_20151217_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(unique=True, max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='recordrequest',
            name='name',
            field=models.CharField(verbose_name='name', help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!", max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], default='unknown.com'),
            preserve_default=False,
        ),
    ]
