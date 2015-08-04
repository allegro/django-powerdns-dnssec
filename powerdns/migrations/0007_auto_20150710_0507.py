# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0006_auto_20150612_0756'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='cryptokey',
            name='modified',
            field=models.DateTimeField(verbose_name='last modified', auto_now=True),
        ),
        migrations.AlterField(
            model_name='domain',
            name='modified',
            field=models.DateTimeField(verbose_name='last modified', auto_now=True),
        ),
        migrations.AlterField(
            model_name='domainmetadata',
            name='modified',
            field=models.DateTimeField(verbose_name='last modified', auto_now=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='modified',
            field=models.DateTimeField(verbose_name='last modified', auto_now=True),
        ),
        migrations.AlterField(
            model_name='supermaster',
            name='modified',
            field=models.DateTimeField(verbose_name='last modified', auto_now=True),
        ),
    ]
