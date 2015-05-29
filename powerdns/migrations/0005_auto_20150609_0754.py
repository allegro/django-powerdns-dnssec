# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0004_auto_20150528_0540'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainTemplate',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordTemplate',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('type', models.CharField(verbose_name='type', max_length=6, help_text='Record type', blank=True, choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')], null=True)),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('content', models.CharField(verbose_name='content', max_length=255)),
                ('ttl', models.PositiveIntegerField(blank=True, default=3600, null=True, verbose_name='TTL', help_text='TTL in seconds')),
                ('prio', models.PositiveIntegerField(blank=True, verbose_name='priority', null=True, help_text='For MX records, this should be the priority of the mail exchanger specified')),
                ('auth', models.NullBooleanField(default=True, verbose_name='authoritative', help_text='Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records')),
                ('remarks', models.TextField(blank=True)),
                ('domain_template', models.ForeignKey(to='powerdns.DomainTemplate')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='domain',
            name='template',
            field=models.ForeignKey(to='powerdns.DomainTemplate', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='record',
            name='template',
            field=models.ForeignKey(to='powerdns.RecordTemplate', blank=True, null=True),
            preserve_default=True,
        ),
    ]
