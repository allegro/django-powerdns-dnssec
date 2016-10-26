# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0029_auto_20160922_0757'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainOwner',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('ownership_type', models.CharField(max_length=10, choices=[('BO', 'Business Owner'), ('TO', 'Technical Owner')], db_index=True)),
                ('domain', models.ForeignKey(to='powerdns.Domain')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='serviceowner',
            old_name='user',
            new_name='owner',
        ),
        migrations.AlterField(
            model_name='service',
            name='owners',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='service_owners', through='powerdns.ServiceOwner'),
        ),
        migrations.AddField(
            model_name='domain',
            name='direct_owners',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='domain_owners', through='powerdns.DomainOwner'),
        ),
    ]
