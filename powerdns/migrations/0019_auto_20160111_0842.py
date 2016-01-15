# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0018_auto_20160105_0824'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domainrequest',
            old_name='account',
            new_name='target_account',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='master',
            new_name='target_master',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='name',
            new_name='target_name',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='record_auto_ptr',
            new_name='target_record_auto_ptr',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='remarks',
            new_name='target_remarks',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='reverse_template',
            new_name='target_reverse_template',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='template',
            new_name='target_template',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='type',
            new_name='target_type',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='unrestricted',
            new_name='target_unrestricted',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='auth',
            new_name='target_auth',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='content',
            new_name='target_content',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='disabled',
            new_name='target_disabled',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='name',
            new_name='target_name',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='ordername',
            new_name='target_ordername',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='prio',
            new_name='target_prio',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='remarks',
            new_name='target_remarks',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='ttl',
            new_name='target_ttl',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='type',
            new_name='target_type',
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='target_owner',
            field=models.ForeignKey(null=True, verbose_name='Owner', related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='target_owner',
            field=models.ForeignKey(null=True, verbose_name='Owner', related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
