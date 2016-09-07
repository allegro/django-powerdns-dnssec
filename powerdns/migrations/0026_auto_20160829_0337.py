# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_auto_20160822_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='type',
            field=models.CharField(help_text='Record qtype', verbose_name='type', max_length=6, null=True, choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')]),
        ),
    ]
