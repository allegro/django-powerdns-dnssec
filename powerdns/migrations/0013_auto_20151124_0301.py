# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.utils
import django.core.validators
import powerdns.models.powerdns
import dj.choices.fields
from django.conf import settings
import powerdns.models.requests


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('powerdns', '0012_auto_20151112_0504'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeleteRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('key', models.CharField(max_length=255, blank=True, null=True)),
                ('target_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('owner', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DomainRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('key', models.CharField(max_length=255, blank=True, null=True)),
                ('name', models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], verbose_name='name')),
                ('master', models.CharField(max_length=128, verbose_name='master', blank=True, null=True)),
                ('type', models.CharField(max_length=6, choices=[('MASTER', 'MASTER'), ('NATIVE', 'NATIVE'), ('SLAVE', 'SLAVE')], verbose_name='type', blank=True, null=True)),
                ('account', models.CharField(max_length=40, verbose_name='account', blank=True, null=True)),
                ('remarks', models.TextField(verbose_name='Additional remarks', blank=True)),
                ('record_auto_ptr', dj.choices.fields.ChoiceField(choices=powerdns.utils.AutoPtrOptions, default=2, help_text='Should A records have auto PTR by default')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecordRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('key', models.CharField(max_length=255, blank=True, null=True)),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], verbose_name='name', blank=True, help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!", max_length=255, null=True)),
                ('type', models.CharField(verbose_name='type', blank=True, help_text='Record qtype', max_length=6, choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')], null=True)),
                ('content', models.CharField(max_length=255, verbose_name='content', blank=True, null=True, help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address")),
                ('ttl', models.PositiveIntegerField(verbose_name='TTL', default=3600, blank=True, null=True, help_text='TTL in seconds')),
                ('prio', models.PositiveIntegerField(verbose_name='priority', blank=True, null=True, help_text='For MX records, this should be the priority of the mail exchanger specified')),
                ('ordername', models.CharField(max_length=255, verbose_name='DNSSEC Order', blank=True, null=True)),
                ('auth', models.NullBooleanField(verbose_name='authoritative', default=True, help_text='Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records')),
                ('disabled', models.BooleanField(verbose_name='Disabled', default=False, help_text='This record should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0')),
                ('remarks', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], verbose_name='name', unique=True),
        ),
        migrations.AlterField(
            model_name='domain',
            name='record_auto_ptr',
            field=dj.choices.fields.ChoiceField(choices=powerdns.utils.AutoPtrOptions, default=2, help_text='Should A records have auto PTR by default'),
        ),
        migrations.AlterField(
            model_name='record',
            name='disabled',
            field=models.BooleanField(verbose_name='Disabled', default=False, help_text='This record should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0'),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='domain',
            field=models.ForeignKey(help_text='The domain for which a record is to be added', related_name='record_requests', to='powerdns.Domain'),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(null=True, blank=True, related_name='requests', help_text='The record for which a change is being requested', to='powerdns.Record'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='domain',
            field=models.ForeignKey(null=True, blank=True, related_name='requests', help_text='The domain for which a change is requested', to='powerdns.Domain'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='parent_domain',
            field=models.ForeignKey(null=True, blank=True, related_name='child_requests', help_text='The parent domain for which a new subdomain is to be created', to='powerdns.Domain'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='reverse_template',
            field=models.ForeignKey(verbose_name='Reverse template', help_text='A template that should be used for reverse domains when PTR templates are automatically created for A records in this template.', blank=True, related_name='reverse_template_for_requests', to='powerdns.DomainTemplate', null=True),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='template',
            field=models.ForeignKey(verbose_name='Template', null=True, blank=True, related_name='template_for_requests', to='powerdns.DomainTemplate'),
        ),
    ]
