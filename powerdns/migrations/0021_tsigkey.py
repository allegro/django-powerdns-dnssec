# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0020_remove_recordrequest_target_ordername'),
    ]

    operations = [
        migrations.CreateModel(
            name='TsigKey',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(help_text='Key name', max_length=255, verbose_name='name')),
                ('algorithm', models.CharField(max_length=50, verbose_name='algorithm', choices=[('hmac-md5', 'hmac-md5')])),
                ('secret', models.CharField(help_text='Secret key', max_length=255, verbose_name='secret')),
            ],
            options={
                'db_table': 'tsigkeys',
            },
        ),
    ]
