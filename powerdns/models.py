# -*- coding: utf-8 -*-
from django.db import models
import time

class Domain(models.Model):
    '''
    PowerDNS domains
    '''
    DOMAIN_TYPE = (
        ('MASTER', 'MASTER'),
        ('NATIVE', 'NATIVE'),
        ('SLAVE', 'SLAVE'),
    )
    name = models.CharField(unique=True, max_length=255)
    master = models.CharField(max_length=128, blank=True, null=True)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6, blank=True, null=True, choices=DOMAIN_TYPE)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'domains'
    def save(self):
        self.name = self.name.lower() # Get rid of CAPs before saving
        super(Domain, self).save() # Call the "real" save() method.


class Record(models.Model):
    '''
    PowerDNS DNS records
    '''
    RECORD_TYPE = (
        ('A', 'A'),
        ('AAAA', 'AAAA'),
        ('CNAME', 'CNAME'),
        ('MX', 'MX'),
        ('NS', 'NS'),
        ('PTR', 'PTR'),
        ('SOA', 'SOA'),
        ('SPF', 'SPF'),
        ('SRV', 'SRV'),
        ('TXT', 'TXT'),
    )
    domain = models.ForeignKey(Domain)
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!")
    type = models.CharField(max_length=6, blank=True, null=True, choices=RECORD_TYPE, help_text='Record qtype')
    content = models.CharField(max_length=255, blank=True, null=True, help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address")
    ttl = models.IntegerField(blank=True, null=True, default='3600', help_text='TTL of this record, in seconds')
    prio = models.IntegerField(blank=True, null=True, help_text='For MX records, this should be the priority of the mail exchanger specified')
    change_date = models.IntegerField(blank=True, null=True, help_text='Set automatically by the system to trigger SOA updates and slave notifications')
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'records'
    def save(self):
        self.name = self.name.lower() # Get rid of CAPs before saving
        self.type = self.type.upper() # CAPITALISE before saving
	# Set change_date to current unix time to allow auto SOA update and slave notification
        self.change_date = int(time.time())
        super(Record, self).save() # Call the "real" save() method.


class Supermaster(models.Model):
    '''
    PowerDNS DNS Servers that should be trusted to push new domains to us
    '''
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True, null=True)
    class Meta:
        db_table = u'supermasters'

