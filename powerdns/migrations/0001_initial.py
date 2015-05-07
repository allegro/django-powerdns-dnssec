# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import powerdns.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified', auto_now_add=True)),
                ('flags', models.PositiveIntegerField(verbose_name='flags')),
                ('active', models.NullBooleanField(verbose_name='active')),
                ('content', models.TextField(null=True, verbose_name='content', blank=True)),
            ],
            options={
                'ordering': ('domain',),
                'db_table': 'cryptokeys',
                'verbose_name': 'crypto key',
                'verbose_name_plural': 'crypto keys',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified', auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='name')),
                ('master', models.CharField(max_length=128, null=True, verbose_name='master', blank=True)),
                ('last_check', models.IntegerField(null=True, verbose_name='last check', blank=True)),
                ('type', models.CharField(blank=True, max_length=6, null=True, verbose_name='type', choices=[('MASTER', 'MASTER'), ('NATIVE', 'NATIVE'), ('SLAVE', 'SLAVE')])),
                ('notified_serial', models.PositiveIntegerField(null=True, verbose_name='notified serial', blank=True)),
                ('account', models.CharField(max_length=40, null=True, verbose_name='account', blank=True)),
            ],
            options={
                'db_table': 'domains',
                'verbose_name': 'domain',
                'verbose_name_plural': 'domains',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DomainMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified', auto_now_add=True)),
                ('kind', models.CharField(max_length=15, verbose_name='kind')),
                ('content', models.TextField(null=True, verbose_name='content', blank=True)),
                ('domain', models.ForeignKey(verbose_name='domain', to='powerdns.Domain')),
            ],
            options={
                'ordering': ('domain',),
                'db_table': 'domainmetadata',
                'verbose_name': 'domain metadata',
                'verbose_name_plural': 'domain metadata',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified', auto_now_add=True)),
                ('name', models.CharField(validators=[powerdns.models.validate_domain_name], max_length=255, blank=True, help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!", null=True, verbose_name='name')),
                ('type', models.CharField(choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')], max_length=6, blank=True, help_text='Record qtype', null=True, verbose_name='type')),
                ('content', models.CharField(validators=[powerdns.models.validate_domain_name], max_length=255, blank=True, help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address", null=True, verbose_name='content')),
                ('number', models.PositiveIntegerField(default=None, editable=False, blank=True, null=True, verbose_name='IP number', db_index=True)),
                ('ttl', models.PositiveIntegerField(default=3600, help_text='TTL in seconds', null=True, verbose_name='TTL', blank=True)),
                ('prio', models.PositiveIntegerField(help_text='For MX records, this should be the priority of the mail exchanger specified', null=True, verbose_name='priority', blank=True)),
                ('change_date', models.PositiveIntegerField(help_text='Set automatically by the system to trigger SOA updates and slave notifications', null=True, verbose_name='change date', blank=True)),
                ('ordername', models.CharField(max_length=255, null=True, verbose_name='DNSSEC Order', blank=True)),
                ('auth', models.NullBooleanField(help_text='Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records', verbose_name='authoritative')),
                ('domain', models.ForeignKey(verbose_name='domain', to='powerdns.Domain')),
            ],
            options={
                'ordering': ('name', 'type'),
                'db_table': 'records',
                'verbose_name': 'record',
                'verbose_name_plural': 'records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SuperMaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified', auto_now_add=True)),
                ('ip', models.CharField(max_length=25, verbose_name='IP')),
                ('nameserver', models.CharField(max_length=255, verbose_name='name server')),
                ('account', models.CharField(max_length=40, null=True, verbose_name='account', blank=True)),
            ],
            options={
                'ordering': ('nameserver', 'account'),
                'db_table': 'supermasters',
                'verbose_name': 'supermaster',
                'verbose_name_plural': 'supermasters',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='supermaster',
            unique_together=set([('nameserver', 'account')]),
        ),
        migrations.AlterUniqueTogether(
            name='record',
            unique_together=set([('name', 'type', 'content')]),
        ),
        migrations.AddField(
            model_name='cryptokey',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='domain', blank=True, to='powerdns.Domain', null=True),
            preserve_default=True,
        ),
    ]
