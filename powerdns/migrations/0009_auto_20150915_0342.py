# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.utils
import django.core.validators
import dj.choices.fields


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0008_auto_20150821_0630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(unique=True, verbose_name='name', max_length=255, validators=[django.core.validators.RegexValidator('^([A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')]),
        ),
        migrations.AlterField(
            model_name='record',
            name='auto_ptr',
            field=dj.choices.fields.ChoiceField(default=2, choices=powerdns.utils.AutoPtrOptions, verbose_name='Auto PTR record'),
        ),
        migrations.AlterField(
            model_name='recordtemplate',
            name='auto_ptr',
            field=dj.choices.fields.ChoiceField(default=2, choices=powerdns.utils.AutoPtrOptions, verbose_name='Auto PTR field'),
        ),
    ]
