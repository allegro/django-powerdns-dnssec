# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0035_auto_20161228_0058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authorisation',
            name='authorised',
        ),
        migrations.RemoveField(
            model_name='authorisation',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='authorisation',
            name='owner',
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(verbose_name='name', unique=True, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], max_length=255),
        ),
        migrations.DeleteModel(
            name='Authorisation',
        ),
    ]
