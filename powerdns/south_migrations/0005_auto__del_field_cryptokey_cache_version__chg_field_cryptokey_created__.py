# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'CryptoKey.cache_version'
        db.delete_column(u'cryptokeys', 'cache_version')


        # Changing field 'CryptoKey.created'
        db.alter_column(u'cryptokeys', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'CryptoKey.modified'
        db.alter_column(u'cryptokeys', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))
        # Deleting field 'SuperMaster.cache_version'
        db.delete_column(u'supermasters', 'cache_version')


        # Changing field 'SuperMaster.created'
        db.alter_column(u'supermasters', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'SuperMaster.modified'
        db.alter_column(u'supermasters', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))
        # Deleting field 'Record.cache_version'
        db.delete_column(u'records', 'cache_version')


        # Changing field 'Record.created'
        db.alter_column(u'records', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'Record.modified'
        db.alter_column(u'records', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))
        # Deleting field 'Domain.cache_version'
        db.delete_column(u'domains', 'cache_version')


        # Changing field 'Domain.created'
        db.alter_column(u'domains', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'Domain.modified'
        db.alter_column(u'domains', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))
        # Deleting field 'DomainMetadata.cache_version'
        db.delete_column(u'domainmetadata', 'cache_version')


        # Changing field 'DomainMetadata.created'
        db.alter_column(u'domainmetadata', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'DomainMetadata.modified'
        db.alter_column(u'domainmetadata', 'modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))

    def backwards(self, orm):
        # Adding field 'CryptoKey.cache_version'
        db.add_column(u'cryptokeys', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'CryptoKey.created'
        db.alter_column(u'cryptokeys', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'CryptoKey.modified'
        db.alter_column(u'cryptokeys', 'modified', self.gf('django.db.models.fields.DateTimeField')())
        # Adding field 'SuperMaster.cache_version'
        db.add_column(u'supermasters', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'SuperMaster.created'
        db.alter_column(u'supermasters', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'SuperMaster.modified'
        db.alter_column(u'supermasters', 'modified', self.gf('django.db.models.fields.DateTimeField')())
        # Adding field 'Record.cache_version'
        db.add_column(u'records', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'Record.created'
        db.alter_column(u'records', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Record.modified'
        db.alter_column(u'records', 'modified', self.gf('django.db.models.fields.DateTimeField')())
        # Adding field 'Domain.cache_version'
        db.add_column(u'domains', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'Domain.created'
        db.alter_column(u'domains', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Domain.modified'
        db.alter_column(u'domains', 'modified', self.gf('django.db.models.fields.DateTimeField')())
        # Adding field 'DomainMetadata.cache_version'
        db.add_column(u'domainmetadata', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'DomainMetadata.created'
        db.alter_column(u'domainmetadata', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'DomainMetadata.modified'
        db.alter_column(u'domainmetadata', 'modified', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        'powerdns.cryptokey': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'CryptoKey', 'db_table': "u'cryptokeys'"},
            'active': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'flags': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'powerdns.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "u'domains'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'master': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notified_serial': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.domainmetadata': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'DomainMetadata', 'db_table': "u'domainmetadata'"},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'powerdns.record': {
            'Meta': {'ordering': "(u'name', u'type')", 'unique_together': "((u'name', u'type', u'content'),)", 'object_name': 'Record', 'db_table': "u'records'"},
            'auth': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'change_date': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'ordername': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'prio': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.supermaster': {
            'Meta': {'ordering': "(u'nameserver', u'account')", 'unique_together': "((u'nameserver', u'account'),)", 'object_name': 'SuperMaster', 'db_table': "u'supermasters'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'nameserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['powerdns']