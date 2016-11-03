# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0005_auto_20150609_0754'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='reverse_template',
            field=models.ForeignKey(blank=True, help_text='A template that should be used for reverse domains when PTR templates are automatically created for A records in this template.', to='powerdns.DomainTemplate', null=True, verbose_name='Reverse template', related_name='reverse_template_for'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='record',
            name='auto_ptr',
            field=models.IntegerField(verbose_name='Auto PTR field', default=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='record',
            name='depends_on',
            field=models.ForeignKey(blank=True, help_text='This record is maintained automatically for another record. It should be automatically updated/deleted. Used for PTR recordsthat depend on A records.', to='powerdns.Record', null=True, verbose_name='Dependent on'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='remarks',
            field=models.TextField(verbose_name='Additional remarks', blank=True),
        ),
        migrations.AlterField(
            model_name='domain',
            name='template',
            field=models.ForeignKey(blank=True, to='powerdns.DomainTemplate', null=True, verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='domaintemplate',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='template',
            field=models.ForeignKey(blank=True, to='powerdns.RecordTemplate', null=True, verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='recordtemplate',
            name='domain_template',
            field=models.ForeignKey(verbose_name='Domain template', to='powerdns.DomainTemplate'),
        ),
        migrations.AlterField(
            model_name='recordtemplate',
            name='remarks',
            field=models.TextField(verbose_name='Additional remarks', blank=True),
        ),
    ]
