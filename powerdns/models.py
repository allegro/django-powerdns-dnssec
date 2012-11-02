# -*- coding: utf-8 -*-

import re
import time

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_ipv4_address
from django.db import models
from django.utils.translation import ugettext_lazy as _


def validate_dns_nodot(value):
    '''
    PowerDNS considers the whole zone to be invalid if any of the records end
    with a period so this custom validator is used to catch them
    '''
    if value.endswith('.'):
        raise ValidationError(u'%s is not allowed to end in a period!' % value)

ipv6_re = re.compile(r'^(?:(?:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){7})|(?:(?!'
                     r'(?:.*[a-f0-9](?::|$)){7,})(?:[a-f0-9]{1,4}(?::[a-f0-9]'
                     r'{1,4}){0,5})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,5})'
                     r'?)))|(?:(?:(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){5}:)|(?:'
                     r'(?!(?:.*[a-f0-9]:){5,})(?:[a-f0-9]{1,4}(?::[a-f0-9]'
                     r'{1,4}){0,3})?::(?:[a-f0-9]{1,4}(?::[a-f0-9]{1,4}){0,3}'
                     r':)?))?(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1[0-9]{2})|(?:'
                     r'[1-9]?[0-9]))(?:\.(?:(?:25[0-5])|(?:2[0-4][0-9])|(?:1'
                     r'[0-9]{2})|(?:[1-9]?[0-9]))){3}))$')
validate_ipv6_address = RegexValidator(
    ipv6_re, _(u'Enter a valid IPv6 address.'), 'invalid',
)


class Domain(models.Model):
    '''
    PowerDNS domains
    '''
    DOMAIN_TYPE = (
        ('MASTER', 'MASTER'),
        ('NATIVE', 'NATIVE'),
        ('SLAVE', 'SLAVE'),
    )
    name = models.CharField(_("name"), unique=True, max_length=255)
    master = models.CharField(
        _("master"), max_length=128, blank=True, null=True,
    )
    last_check = models.IntegerField(_("last check"), blank=True, null=True)
    type = models.CharField(
        _("type"), max_length=6, blank=True, null=True, choices=DOMAIN_TYPE,
    )
    notified_serial = models.PositiveIntegerField(
        _("notified serial"), blank=True, null=True,
    )
    account = models.CharField(
        _("account"), max_length=40, blank=True, null=True,
    )

    class Meta:
        db_table = u'domains'
        verbose_name = _("domain")
        verbose_name_plural = _("domains")

    def __unicode__(self):
        return self.name

    def clean(self):
        self.name = self.name.lower()


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
    domain = models.ForeignKey(Domain, verbose_name=_("domain"))
    name = models.CharField(
        _("name"), max_length=255, blank=True, null=True,
        validators=[validate_dns_nodot],
        help_text=_("Actual name of a record. Must not end in a '.' and be"
                    " fully qualified - it is not relative to the name of the"
                    " domain!"),
    )
    type = models.CharField(
        _("type"), max_length=6, blank=True, null=True,
        choices=RECORD_TYPE, help_text=_("Record qtype"),
    )
    content = models.CharField(
        _("content"), max_length=255, blank=True, null=True,
        validators=[validate_dns_nodot],
        help_text=_("The 'right hand side' of a DNS record. For an A"
                    " record, this is the IP address"),
    )
    ttl = models.PositiveIntegerField(
        _("TTL"), blank=True, null=True, default=3600,
        help_text=_("TTL in seconds"),
    )
    prio = models.PositiveIntegerField(
        _("priority"), blank=True, null=True,
        help_text=_("For MX records, this should be the priority of the"
                    " mail exchanger specified"),
    )
    change_date = models.PositiveIntegerField(
        _("change date"), _blank=True, null=True,
        help_text=_("Set automatically by the system to trigger SOA"
                    " updates and slave notifications"),
    )
    ordername = models.CharField(
        _("DNSSEC Order"), max_length=255, blank=True, null=True,
    )
    auth = models.NullBooleanField(
        _("authoritative"),
        help_text=_("Should be set for data for which is itself"
                    " authoritative, which includes the SOA record and our own"
                    " NS records but not set for NS records which are used for"
                    " delegation or any delegation related glue (A, AAAA)"
                    " records"),
    )

    class Meta:
        db_table = u'records'
        ordering = ('name', 'type')
        unique_together = ('name', 'type', 'content')
        verbose_name = _("record")
        verbose_name_plural = _("records")

    def __unicode__(self):
        return self.name

    def _generate_ordername(self):
        '''
        Check which DNSSEC Mode the domain is in and fill the `ordername`
        field depending on the mode.
        '''
        q1 = DomainMetadata.objects.filter(domain=self.domain)
        if not len(q1) == 0:
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
        In 'NSEC3' non-narrow mode, the ordername should contain a lowercase
        base32hex encoded representation of the salted & iterated hash of the
        full record name.  "pdnssec hash-zone-record zone record" can be used
        to calculate this hash.
        '''
        return 'FIXME'  # FIXME: Implement ordername_nsec3.

    def _generate_ordername_nsec3_narrow(self):
        '''
        When running in NSEC3 'Narrow' mode, the ordername field is ignored and
        best left empty.
        '''
        return None

    def clean(self):
        if self.type == 'A':
            validate_ipv4_address(self.content)
        if self.type == 'AAAA':
            validate_ipv6_address(self.content)
        if self.name:
            self.name = self.name.lower()
        if self.type:
            self.type = self.type.upper()

    def save(self, *args, **kwargs):
        self.change_date = int(time.time())
        self.ordername = self._generate_ordername()
        super(Record, self).save(*args, **kwargs)


class SuperMaster(models.Model):
    '''
    PowerDNS DNS Servers that should be trusted to push new domains to us
    '''
    ip = models.CharField(_("IP"), max_length=25)
    nameserver = models.CharField(_("name server"), max_length=255)
    account = models.CharField(
        _("account"), max_length=40, blank=True, null=True,
    )

    class Meta:
        db_table = u'supermasters'
        ordering = ('nameserver', 'account')
        unique_together = ('nameserver', 'account')
        verbose_name = _("supermaster")
        verbose_name_plural = _("supermasters")

    def __unicode__(self):
        return self.ip


class DomainMetadata(models.Model):
    domain = models.ForeignKey(Domain, verbose_name=_("domain"))
    kind = models.CharField(_("kind"), max_length=15)
    content = models.TextField(_("content"), blank=True, null=True)

    class Meta:
        db_table = u'domainmetadata'
        ordering = ('domain',)
        verbose_name = _("domain metadata")
        verbose_name_plural = _("domain metadata")

    def __unicode__(self):
        return unicode(self.domain)


class CryptoKey(models.Model):
    domain = models.ForeignKey(
        Domain, verbose_name=_("domain"), blank=True, null=True,
        on_delete=models.SET_NULL,
    )
    flags = models.PositiveIntegerField(_("flags"))
    active = models.NullBooleanField(_("active"))
    content = models.TextField(_("content"), blank=True, null=True)

    class Meta:
        db_table = u'cryptokeys'
        ordering = ('domain',)
        verbose_name = _("crypto key")
        verbose_name_plural = _("crypto keys")

    def __unicode__(self):
        return unicode(self.domain)
