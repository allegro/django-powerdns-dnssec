# -*- coding: utf-8 -*-

import base64
import hashlib
import string
import time

import ipaddr

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address
from django.db import models
from django.utils.translation import ugettext_lazy as _


RECORD_TYPES = (
    'A', 'AAAA', 'CERT', 'CNAME', 'DNSKEY', 'DS', 'HINFO', 'KEY', 'LOC', 'MX',
    'NAPTR', 'NS', 'NSEC', 'PTR', 'RP', 'RRSIG', 'SOA', 'SPF', 'SSHFP', 'SRV',
    'TXT',
)

try:
    RECORD_TYPES = settings.POWERDNS_RECORD_TYPES
except AttributeError:
    pass

# http://tools.ietf.org/html/rfc4648#section-7
b32_trans = string.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                             '0123456789ABCDEFGHIJKLMNOPQRSTUV')


def validate_dns_nodot(value):
    '''
    PowerDNS considers the whole zone to be invalid if any of the records end
    with a period so this custom validator is used to catch them
    '''
    if value.endswith('.'):
        raise ValidationError(
            _(u'%s is not allowed to end in a period!') % value,
            code='invalid',
        )


def validate_ipv6_address(value):
    try:
        ipaddr.IPv6Address(value)
    except ipaddr.AddressValueError:
        raise ValidationError(
            _(u'Enter a valid IPv6 address.'), code='invalid',
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
    RECORD_TYPE = [(r, r) for r in RECORD_TYPES]
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
        _("change date"), blank=True, null=True,
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
        if self.prio is not None:
            content = "%d %s" % (self.prio, self.content)
        else:
            content = self.content
        return "%s IN %s %s" % (self.name, self.type, content)

    def _generate_ordername(self):
        '''
        Check which DNSSEC Mode the domain is in and fill the `ordername`
        field depending on the mode.
        '''
        cryptokey = CryptoKey.objects.filter(domain=self.domain)
        if not cryptokey.count():
            return None
        metadata = DomainMetadata.objects.filter(domain=self.domain)
        nsec3param = metadata.filter(kind='NSEC3PARAM')
        nsec3narrow = metadata.filter(kind='NSEC3NARROW')
        if nsec3param.count():
            if nsec3narrow.count():
                # When running in NSEC3 'Narrow' mode, the ordername field is
                # ignored and best left empty.
                return ''
            return self._generate_ordername_nsec3(nsec3param[0])
        return self._generate_ordername_nsec()

    def _generate_ordername_nsec(self):
        '''
        In 'NSEC' mode, it should contain the relative part of a domain name,
        in reverse order, with dots replaced by spaces
        '''
        domain_words = self.domain.name.split('.')
        host_words = self.name.split('.')
        relative_word_count = len(host_words) - len(domain_words)
        relative_words = host_words[0:relative_word_count]
        ordername = ' '.join(relative_words[::-1])
        return ordername

    def _generate_ordername_nsec3(self, nsec3param):
        '''
        In 'NSEC3' non-narrow mode, the ordername should contain a lowercase
        base32hex encoded representation of the salted & iterated hash of the
        full record name.  "pdnssec hash-zone-record zone record" can be used
        to calculate this hash.
        '''
        try:
            algo, flags, iterations, salt = nsec3param.content.split()
            if algo != '1':
                raise ValueError("Incompatible hash algorithm.")
            if flags != '1':
                raise ValueError("Incompatible flags.")
            salt = salt.decode('hex')
            # convert the record name to the DNSSEC canonical form, e.g.
            # a format suitable for digesting in hashes
            record_name = '%s.' % self.name.lower().rstrip('.')
            parts = ["%s%s" % (chr(len(x)), x) for x in record_name.split('.')]
            record_name = ''.join(parts)
        except (ValueError, TypeError, AttributeError):
            return None  # incompatible input
        record_name = self._sha1(record_name, salt)
        i = 0
        while i < int(iterations):
            record_name = self._sha1(record_name, salt)
            i += 1
        result = base64.b32encode(record_name)
        result = result.translate(b32_trans)
        return result.lower()

    def _sha1(self, value, salt):
        s = hashlib.sha1()
        s.update(value)
        s.update(salt)
        return s.digest()

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
