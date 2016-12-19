# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0007_auto_20150710_0507'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordtemplate',
            name='auto_ptr',
            field=models.IntegerField(default=2, verbose_name='Auto PTR field'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='record',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
