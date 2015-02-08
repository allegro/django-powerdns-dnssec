# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Domain'
        db.create_table(u'domains', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('master', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('last_check', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('notified_serial', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('account', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('powerdns', ['Domain'])

        # Adding model 'Record'
        db.create_table(u'records', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['powerdns.Domain'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default='3600', null=True, blank=True)),
            ('prio', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('change_date', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('powerdns', ['Record'])

        # Adding model 'Supermaster'
        db.create_table(u'supermasters', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('nameserver', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('account', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('powerdns', ['Supermaster'])


    def backwards(self, orm):
        
        # Deleting model 'Domain'
        db.delete_table(u'domains')

        # Deleting model 'Record'
        db.delete_table(u'records')

        # Deleting model 'Supermaster'
        db.delete_table(u'supermasters')


    models = {
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
        'powerdns.record': {
            'Meta': {'object_name': 'Record', 'db_table': "u'records'"},
            'change_date': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powerdns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'prio': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': "'3600'", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        'powerdns.supermaster': {
            'Meta': {'object_name': 'Supermaster', 'db_table': "u'supermasters'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'nameserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['powerdns']
