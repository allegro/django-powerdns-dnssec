# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, validate_ipv4_address

import re
import time

def validate_dns_nodot(value):
    '''
    PowerDNS considers the whole zone to be invalid if any of the records end with a period
    so this custom validator is used to catch them
    '''
    if value.endswith('.'):
        raise ValidationError(u'%s is not allowed to end in a period!' % value)

ipv6_re = re.compile(r'^(?:(?:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){7})|(?:(?!(?:.*[a-f0-9](?::|$)){7,})(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})?)))|(?:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){5}:)|(?:(?!(?:.*[a-f0-9]:){5,})(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3}:)?))?(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:[1-9]?[0-9]))(?:\.(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:[1-9]?[0-9]))){3}))$')
validate_ipv6_address = RegexValidator(ipv6_re, _(u'Enter a valid IPv6 address.'), 'invalid')


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
    notified_serial = models.PositiveIntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'domains'
    def clean(self):
        self.name = self.name.lower() # Get rid of CAPs before saving

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
    name = models.CharField(max_length=255, blank=True, null=True, validators=[validate_dns_nodot], help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!")
    type = models.CharField(max_length=6, blank=True, null=True, choices=RECORD_TYPE, help_text='Record qtype')
    content = models.CharField(max_length=255, blank=True, null=True, validators=[validate_dns_nodot], help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address")
    ttl = models.PositiveIntegerField(blank=True, null=True, default='3600', help_text='TTL of this record, in seconds')
    prio = models.PositiveIntegerField(blank=True, null=True, help_text='For MX records, this should be the priority of the mail exchanger specified')
    change_date = models.PositiveIntegerField(blank=True, null=True, help_text='Set automatically by the system to trigger SOA updates and slave notifications')
    ordername = models.CharField(max_length=255, blank=True, null=True,)
    auth = models.NullBooleanField()
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'records'
    def clean(self):
        if self.type == 'A':
            validate_ipv4_address(self.content)
        if self.type == 'AAAA':
            validate_ipv6_address(self.content)
        if self.name:
            self.name = self.name.lower() # Get rid of CAPs before saving
        if self.type:
            self.type = self.type.upper() # CAPITALISE before saving
    def save(self):
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

class Domainmetadata(models.Model):
    domain_id = models.PositiveIntegerField()
    kind = models.CharField(max_length=15)
    content = models.TextField(blank=True, null=True)
    class Meta:
        db_table = u'domainmetadata'

class Cryptokey(models.Model):
    domain_id = models.PositiveIntegerField(blank=True, null=True, default=None,)
    flags = models.PositiveIntegerField()
    active = models.NullBooleanField()
    content = models.TextField(blank=True, null=True)
    class Meta:
        db_table = u'cryptokeys'


