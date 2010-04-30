# -*- coding: utf-8 -*-
from django.db import models

class Domain(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    master = models.CharField(max_length=128, blank=True, null=True)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6, blank=True, null=True)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'domains'

class Record(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.ForeignKey(Domain)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=6, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)
    ttl = models.IntegerField(blank=True, null=True)
    prio = models.IntegerField(blank=True, null=True)
    change_date = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'records'

class Supermaster(models.Model):
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True, null=True)
    class Meta:
        db_table = u'supermasters'
