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
    ttl = models.PositiveIntegerField("TTL", blank=True, null=True, default='3600', help_text='TTL in seconds')
    prio = models.PositiveIntegerField("Priority", blank=True, null=True, help_text='For MX records, this should be the priority of the mail exchanger specified')
    change_date = models.PositiveIntegerField(blank=True, null=True, help_text='Set automatically by the system to trigger SOA updates and slave notifications')
    ordername = models.CharField("DNSSEC Order", max_length=255, blank=True, null=True,)
    auth = models.NullBooleanField("Authoritative", help_text="Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records")
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'records'
        ordering = ('name', 'type')
        unique_together = ('name', 'type', 'content')
    def _generate_ordername(self):
        "The 'ordername' field needs to be filled out depending on the NSEC/NSEC3 mode."
        '''Check which DNSSEC Mode the domain is in'''
        q1 = DomainMetadata.objects.filter(domain=self.domain)
        if len(q1) == 0:
            '''We are not in NSEC3 mode so it must be NSEC'''
            print "DEBUG: MODE is NSEC"
            return self._generate_ordername_nsec()
        try:
            '''Check is a NSEC3NARROW record exists'''
            mode = q1.get(kind='NSEC3NARROW').kind
            print "DEBUG: MODE is NSEC3NARROW"
            return self._generate_ordername_nsec3_narrow()
        except:
            '''We seem to be in NSEC3 non-narrow mode'''
            print "DEBUG: MODE is NSEC3"
            return self._generate_ordername_nsec3()

    def _generate_ordername_nsec(self):
        '''
        In 'NSEC' mode, it should contain the relative part of a domain name,
        in reverse order, with dots replaced by spaces
        '''
        domain_words = self.domain.name.split('.')
        host_words = self.name.split('.')
        print len(domain_words), domain_words
        print len(host_words), host_words
        relative_word_no = len(host_words) - len(domain_words)
        relative_words = host_words[0:relative_word_no]
        relative_words.reverse()
        print "DEBUG Host words:", relative_words
        ordername = ' '.join(relative_words)
        return ordername
    def _generate_ordername_nsec3(self):
        '''
        In 'NSEC3' non-narrow mode, the ordername should contain a lowercase base32hex encoded
        representation of the salted & iterated hash of the full record name.
        "pdnssec hash-zone-record zone record" can be used to calculate this hash.
        '''
        # FIXME
        return 'FIXME'
    def _generate_ordername_nsec3_narrow(self):
        "When running in NSEC3 'Narrow' mode, the ordername field is ignored and best left empty."
        return None
    def clean(self):
        if self.type == 'A':
            validate_ipv4_address(self.content)
        if self.type == 'AAAA':
            validate_ipv6_address(self.content)
        if self.name:
            self.name = self.name.lower() # Get rid of CAPs before saving
        if self.type:
            self.type = self.type.upper() # CAPITALISE before saving
    def save(self, *args, **kwargs):
        # Set change_date to current unix time to allow auto SOA update and slave notification
        self.change_date = int(time.time())
        ## The 'ordername' field needs to be filled out depending on the NSEC/NSEC3 mode.
        self.ordername = self._generate_ordername()
        super(Record, self).save(*args, **kwargs) # Call the "real" save() method.


class SuperMaster(models.Model):
    '''
    PowerDNS DNS Servers that should be trusted to push new domains to us
    '''
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True, null=True)
    def __unicode__(self):
        return self.ip
    class Meta:
        db_table = u'supermasters'
        ordering = ('nameserver', 'account')
        unique_together = ('nameserver', 'account')

class DomainMetadata(models.Model):
    domain = models.ForeignKey(Domain)
    kind = models.CharField(max_length=15)
    content = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.domain.__unicode__()
    class Meta:
        verbose_name_plural = 'Domain metadata'
        db_table = u'domainmetadata'
        ordering = ('domain',)

class CryptoKey(models.Model):
    domain = models.ForeignKey(Domain)
    ## TODO: When Django 1.3 is released use this instead..
    # domain = models.ForeignKey(Domain, blank=True, null=True, on_delete=models.SET_NULL)
    flags = models.PositiveIntegerField()
    active = models.NullBooleanField()
    content = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.domain.__unicode__()
    class Meta:
        db_table = u'cryptokeys'
        ordering = ('domain',)


