# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import powerdns.models.powerdns


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0014_auto_20151124_0505'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='unrestricted',
            field=models.BooleanField(default=False, verbose_name='Unrestricted', help_text="Can users that are not owners of this domain add recordsto it without owner's permission?"),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='unrestricted',
            field=models.BooleanField(default=False, verbose_name='Unrestricted', help_text="Can users that are not owners of this domain add recordsto it without owner's permission?"),
        ),
        migrations.AddField(
            model_name='domaintemplate',
            name='unrestricted',
            field=models.BooleanField(default=False, verbose_name='Unrestricted', help_text="Can users that are not owners of this domain add recordsto it without owner's permission?"),
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], unique=True, verbose_name='name'),
        ),
    ]
