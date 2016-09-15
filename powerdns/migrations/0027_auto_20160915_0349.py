# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0026_auto_20160829_0337'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('uid', models.CharField(max_length=100, db_index=True, unique=True)),
                ('status', models.CharField(max_length=100, db_index=True, choices=[('ACTIVE', 'Active'), ('OBSOLETE', 'Obsolete'), ('PENDING_OBSOLESCENCE', 'Pending Obsolescence'), ('PLANNING', 'Planning'), ('PENDING', 'Pending')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceOwner',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('ownership_type', models.CharField(max_length=10, db_index=True, choices=[('BO', 'Business Owner'), ('TO', 'Technical Owner')])),
                ('service', models.ForeignKey(to='powerdns.Service')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='service',
            name='owners',
            field=models.ManyToManyField(through='powerdns.ServiceOwner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domain',
            name='service',
            field=models.ForeignKey(blank=True, null=True, to='powerdns.Service'),
        ),
        migrations.AddField(
            model_name='record',
            name='service',
            field=models.ForeignKey(blank=True, null=True, to='powerdns.Service'),
        ),
    ]
