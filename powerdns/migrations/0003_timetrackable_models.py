# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CryptoKey.created'
        db.add_column(u'cryptokeys', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'CryptoKey.modified'
        db.add_column(u'cryptokeys', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'CryptoKey.cache_version'
        db.add_column(u'cryptokeys', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'SuperMaster.created'
        db.add_column(u'supermasters', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'SuperMaster.modified'
        db.add_column(u'supermasters', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'SuperMaster.cache_version'
        db.add_column(u'supermasters', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Record.created'
        db.add_column(u'records', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Record.modified'
        db.add_column(u'records', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Record.cache_version'
        db.add_column(u'records', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Domain.created'
        db.add_column(u'domains', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Domain.modified'
        db.add_column(u'domains', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Domain.cache_version'
        db.add_column(u'domains', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'DomainMetadata.created'
        db.add_column(u'domainmetadata', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'DomainMetadata.modified'
        db.add_column(u'domainmetadata', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'DomainMetadata.cache_version'
        db.add_column(u'domainmetadata', 'cache_version',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CryptoKey.created'
        db.delete_column(u'cryptokeys', 'created')

        # Deleting field 'CryptoKey.modified'
        db.delete_column(u'cryptokeys', 'modified')

        # Deleting field 'CryptoKey.cache_version'
        db.delete_column(u'cryptokeys', 'cache_version')

        # Deleting field 'SuperMaster.created'
        db.delete_column(u'supermasters', 'created')

        # Deleting field 'SuperMaster.modified'
        db.delete_column(u'supermasters', 'modified')

        # Deleting field 'SuperMaster.cache_version'
        db.delete_column(u'supermasters', 'cache_version')

        # Deleting field 'Record.created'
        db.delete_column(u'records', 'created')

        # Deleting field 'Record.modified'
        db.delete_column(u'records', 'modified')

        # Deleting field 'Record.cache_version'
        db.delete_column(u'records', 'cache_version')

        # Deleting field 'Domain.created'
        db.delete_column(u'domains', 'created')

        # Deleting field 'Domain.modified'
        db.delete_column(u'domains', 'modified')

        # Deleting field 'Domain.cache_version'
        db.delete_column(u'domains', 'cache_version')

        # Deleting field 'DomainMetadata.created'
        db.delete_column(u'domainmetadata', 'created')

        # Deleting field 'DomainMetadata.modified'
        db.delete_column(u'domainmetadata', 'modified')

        # Deleting field 'DomainMetadata.cache_version'
        db.delete_column(u'domainmetadata', 'cache_version')


    models = {
        'powerdns.cryptokey': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'CryptoKey', 'db_table': "u'cryptokeys'"},
            'active': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'flags': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'powerdns.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "u'domains'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'master': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notified_serial': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.domainmetadata': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'DomainMetadata', 'db_table': "u'domainmetadata'"},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'powerdns.record': {
            'Meta': {'ordering': "('name', 'type')", 'unique_together': "(('name', 'type', 'content'),)", 'object_name': 'Record', 'db_table': "u'records'"},
            'auth': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'change_date': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ordername': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'prio': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3600', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.supermaster': {
            'Meta': {'ordering': "('nameserver', 'account')", 'unique_together': "(('nameserver', 'account'),)", 'object_name': 'SuperMaster', 'db_table': "u'supermasters'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'nameserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['powerdns']