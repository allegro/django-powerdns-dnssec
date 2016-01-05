# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.models.powerdns
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0017_auto_20160104_0642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], verbose_name='name', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='recordrequest',
            name='type',
            field=models.CharField(verbose_name='type', default='TXT', choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')], max_length=6, help_text='Record qtype'),
            preserve_default=False,
        ),
    ]
