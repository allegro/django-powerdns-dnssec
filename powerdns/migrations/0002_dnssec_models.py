# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CryptoKey'
        db.create_table(u'cryptokeys', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['powerdns.Domain'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('flags', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('active', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('powerdns', ['CryptoKey'])

        # Adding model 'DomainMetadata'
        db.create_table(u'domainmetadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['powerdns.Domain'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('powerdns', ['DomainMetadata'])

        # Adding unique constraint on 'SuperMaster', fields ['nameserver', 'account']
        db.create_unique(u'supermasters', ['nameserver', 'account'])

        # Adding field 'Record.ordername'
        db.add_column(u'records', 'ordername',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Record.auth'
        db.add_column(u'records', 'auth',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'Record', fields ['content', 'type', 'name']
        db.create_unique(u'records', ['content', 'type', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Record', fields ['content', 'type', 'name']
        db.delete_unique(u'records', ['content', 'type', 'name'])

        # Removing unique constraint on 'SuperMaster', fields ['nameserver', 'account']
        db.delete_unique(u'supermasters', ['nameserver', 'account'])

        # Deleting model 'CryptoKey'
        db.delete_table(u'cryptokeys')

        # Deleting model 'DomainMetadata'
        db.delete_table(u'domainmetadata')

        # Deleting field 'Record.ordername'
        db.delete_column(u'records', 'ordername')

        # Deleting field 'Record.auth'
        db.delete_column(u'records', 'auth')


    models = {
        'powerdns.cryptokey': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'CryptoKey', 'db_table': "u'cryptokeys'"},
            'active': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'flags': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'powerdns.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "u'domains'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'master': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notified_serial': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.domainmetadata': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'DomainMetadata', 'db_table': "u'domainmetadata'"},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'powerdns.record': {
            'Meta': {'ordering': "('name', 'type')", 'unique_together': "(('name', 'type', 'content'),)", 'object_name': 'Record', 'db_table': "u'records'"},
            'auth': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'change_date': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ordername': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'prio': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.supermaster': {
            'Meta': {'ordering': "('nameserver', 'account')", 'unique_together': "(('nameserver', 'account'),)", 'object_name': 'SuperMaster', 'db_table': "u'supermasters'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'nameserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['powerdns']