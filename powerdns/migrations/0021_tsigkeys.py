# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0020_remove_recordrequest_target_ordername'),
    ]

    operations = [
        migrations.CreateModel(
            name='TsigKeys',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('algorithm', models.CharField(verbose_name='algorithm', max_length=50, choices=[('hmac-md5', 'hmac-md5')])),
                ('secret', models.CharField(verbose_name='secret', max_length=255)),
            ],
            options={
                'db_table': 'tsigkeys',
            },
        ),
    ]
