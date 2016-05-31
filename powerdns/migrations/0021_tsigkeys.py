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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255, help_text='Key name', verbose_name='name')),
                ('algorithm', models.CharField(max_length=50, verbose_name='algorithm', choices=[('hmac-md5', 'hmac-md5')])),
                ('secret', models.CharField(max_length=255, help_text='Secret key', verbose_name='secret')),
            ],
            options={
                'db_table': 'tsigkeys',
            },
        ),
    ]
