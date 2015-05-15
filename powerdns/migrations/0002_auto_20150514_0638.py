# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='disabled',
            field=models.BooleanField(verbose_name='Disabled', help_text='This field should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^[A-Za-z][A-Za-z1-9.-]*[A-Za-z1-9]$')], verbose_name='name', unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='content',
            field=models.CharField(null=True, verbose_name='content', max_length=255, blank=True, help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address"),
        ),
    ]
