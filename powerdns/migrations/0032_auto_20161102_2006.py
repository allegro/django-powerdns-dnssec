# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0031_auto_20161102_0640'),
    ]

    operations = [
        migrations.AddField(
            model_name='deleterequest',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created', default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deleterequest',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='last modified', default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created', default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='last modified', default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created', default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='last modified', default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=False,
        ),
    ]
