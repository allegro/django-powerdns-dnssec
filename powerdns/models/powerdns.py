import base64
import hashlib
import sys
import time

import rules
from dj.choices.fields import ChoiceField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core.urlresolvers import reverse
from IPy import IP
from threadlocals.threadlocals import get_current_user

from powerdns.utils import (
    AutoPtrOptions,
    is_authorised,
    is_owner,
    no_object,
    Owned,
    RecordLike,
    TimeTrackable,
    to_reverse,
    validate_domain_name,
)


BASIC_RECORD_TYPES = (
    'A', 'AAAA', 'CNAME', 'HINFO', 'MX', 'NAPTR', 'NS', 'PTR', 'SOA', 'SRV',
    'TXT',
)

DNSSEC_RECORD_TYPES = ('DNSKEY', 'DS', 'KEY', 'NSEC', 'RRSIG')

AUX_RECORD_TYPES = ('AFSDB', 'CERT', 'LOC', 'RP', 'SPF', 'SSHFP')

RECORD_TYPES = sorted(set(
    BASIC_RECORD_TYPES + DNSSEC_RECORD_TYPES + AUX_RECORD_TYPES
))


# If we try get the domain in the global scope then removing it
# would be unrecoverable. Thus this little helper function.

DEFAULT_REVERSE_DOMAIN_TEMPLATE = None


can_edit = rules.is_superuser | no_object | is_owner | is_authorised
can_delete = rules.is_superuser | is_owner | is_authorised


def get_default_reverse_domain():
    """Returns a default reverse domain."""
    from powerdns.models.templates import DomainTemplate
    global DEFAULT_REVERSE_DOMAIN_TEMPLATE
    if not DEFAULT_REVERSE_DOMAIN_TEMPLATE:
        DEFAULT_REVERSE_DOMAIN_TEMPLATE = DomainTemplate.objects.get(
            name=settings.DNSAAS_DEFAULT_REVERSE_DOMAIN_TEMPLATE
        )
    return DEFAULT_REVERSE_DOMAIN_TEMPLATE


try:
    RECORD_TYPES = settings.POWERDNS_RECORD_TYPES
except AttributeError:
    pass

# http://tools.ietf.org/html/rfc4648#section-7
if sys.version_info[0] == 2:
    import string
    maketrans_func = string.maketrans
else:
    maketrans_func = str.maketrans
b32_trans = maketrans_func(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
    '0123456789ABCDEFGHIJKLMNOPQRSTUV'
)

# Validator for the domain names only in RFC-1035
# PowerDNS considers the whole zone to be invalid if any of the records end
# with a period so this custom validator is used to catch them


# This is a class for historical reasons in order not to break migrations
@deconstructible
class SubDomainValidator():
    def __call__(self, domain_name):
        """Validates if a not authorised user tries to subdomain a domain she
        can't edit"""
        user = get_current_user()
        if rules.is_superuser(user):
            return domain_name
        domain_bits = domain_name.split('.')
        for i in range(-len(domain_bits), 0):
            super_domain = '.'.join(domain_bits[i:])
            try:
                super_domain = Domain.objects.get(name=super_domain)
            except Domain.DoesNotExist:
                continue
            if can_edit(user, super_domain):
                # ALLOW - this user owns a superdomain
                return domain_name
            else:
                # DENY - this user doesn't own a superdomain
                raise ValidationError(
                    "You don't have a permission to create a subdomain in {}".
                    format(super_domain)
                )
        # Fallthrough - ALLOW - we don't manage any superdomain
        return domain_name

    def __eq__(self, other):
        return type(self) == type(other)


class WithRequests(models.Model):

    class Meta:
        abstract = True

    def request_factory(operation):
        def result(self):
            def fmt(str_, **kwargs):
                return str_.format(
                    obj=type(self)._meta.object_name.lower(),
                    opr=operation,
                    **kwargs
                )

            if get_current_user().has_perm(
                fmt('powerdns.{opr}_{obj}'),
                self
            ):
                return '<a href={}>{}</a>'.format(
                    reverse(
                        fmt('admin:powerdns_{obj}_{opr}'),
                        args=(self.pk,)
                    ),
                    operation.capitalize()
                )
            if operation == 'delete':
                return '<a href="{}">Request deletion</a>'.format(
                    reverse(
                        fmt('admin:powerdns_deleterequest_add')
                    ) + '?target_id={}&content_type={}'.format(
                        self.pk,
                        ContentType.objects.get_for_model(type(self)).pk,
                    )
                )

            return '<a href="{}">Request change</a>'.format(
                reverse(
                    fmt('admin:powerdns_{obj}request_add')
                ) + '?{}={}'.format(
                    type(self)._meta.object_name.lower(),
                    self.pk
                )
            )
        result.allow_tags = True
        result.__name__ = 'request_' + operation
        return result

    request_change = request_factory('change')
    request_deletion = request_factory('delete')


class Domain(TimeTrackable, Owned, WithRequests):
    '''
    PowerDNS domains
    '''
    DOMAIN_TYPE = (
        ('MASTER', 'MASTER'),
        ('NATIVE', 'NATIVE'),
        ('SLAVE', 'SLAVE'),
    )
    copy_fields = ['record_auto_ptr']
    name = models.CharField(
        _("name"),
        unique=True,
        max_length=255,
        validators=[validate_domain_name, SubDomainValidator()]
    )
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
    remarks = models.TextField(_('Additional remarks'), blank=True)
    template = models.ForeignKey(
        'powerdns.DomainTemplate',
        verbose_name=_('Template'),
        blank=True,
        null=True,
    )
    reverse_template = models.ForeignKey(
        'powerdns.DomainTemplate',
        verbose_name=_('Reverse template'),
        blank=True,
        null=True,
        related_name='reverse_template_for',
        help_text=_(
            'A template that should be used for reverse domains when '
            'PTR templates are automatically created for A records in this '
            'template.'
        )
    )
    record_auto_ptr = ChoiceField(
        choices=AutoPtrOptions,
        default=AutoPtrOptions.ALWAYS,
        help_text=_(
            'Should A records have auto PTR by default'
        )
    )

    unrestricted = models.BooleanField(
        _('Unrestricted'),
        null=False,
        default=False,
        help_text=_(
            "Can users that are not owners of this domain add records"
            "to it without owner's permission?"
        )
    )

    class Meta:
        db_table = u'domains'
        verbose_name = _("domain")
        verbose_name_plural = _("domains")

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.lower()

    def save(self, *args, **kwargs):
        # This save can trigger creating some templated records.
        # So we do it atomically
        with transaction.atomic():
            super(Domain, self).save(*args, **kwargs)

    def get_soa(self):
        """Returns the SOA record for this domain"""
        try:
            return Record.objects.get(type='SOA', domain=self)
        except Record.DoesNotExist:
            return

    def add_record_url(self, authorised):
        """Return URL for 'Add record' action"""
        model = 'record' if authorised else 'recordrequest'
        return (
            reverse('admin:powerdns_{}_add'.format(model)) +
            '?domain={}'.format(self.pk)
        )

    def add_record_link(self):
        authorised = get_current_user().has_perm(
            'powerdns.change_domain', self
        ) or self.unrestricted
        return '<a href="{}">{}</a>'.format(
            self.add_record_url(authorised),
            ('Add record' if authorised else 'Request record')
        )

    add_record_link.allow_tags = True

    def extra_buttons(self):
        authorised = get_current_user().has_perm(
            'powerdns.change_domain', self
        )
        yield (self.add_record_url(authorised), 'Add record')

    def can_auto_accept(self, user):
        return (
            user.is_superuser or
            self.unrestricted or
            user == self.owner or
            user.id in self.authorisations.values_list(
                'authorised', flat=True
            )
        )

    def as_empty_history(self):
        """We don't care about domain history for now"""
        return {}

    def as_history_dump(self):
        """We don't care about domain history for now"""
        return {}


rules.add_perm('powerdns', rules.is_authenticated)
rules.add_perm('powerdns.add_domain', rules.is_superuser)
rules.add_perm('powerdns.change_domain', can_edit)
rules.add_perm('powerdns.delete_domain', can_delete)


class Record(TimeTrackable, Owned, RecordLike, WithRequests):
    '''
    PowerDNS DNS records
    '''
    prefix = ''
    RECORD_TYPE = [(r, r) for r in RECORD_TYPES]
    domain = models.ForeignKey(
        Domain,
        verbose_name=_("domain"),
    )
    name = models.CharField(
        _("name"),
        max_length=255,
        blank=False,
        null=False,
        validators=[validate_domain_name],
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
        help_text=_("The 'right hand side' of a DNS record. For an A"
                    " record, this is the IP address"),
    )
    number = models.PositiveIntegerField(
        _("IP number"), null=True, blank=True, default=None, editable=False,
        db_index=True
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
        default=True,
    )
    disabled = models.BooleanField(
        _("Disabled"),
        help_text=_(
            "This record should not be used for actual DNS queries."
            " Note - this field works for pdns >= 3.4.0"
        ),
        default=False,
    )

    remarks = models.TextField(blank=True)
    template = models.ForeignKey(
        'powerdns.RecordTemplate',
        verbose_name=_('Template'),
        blank=True,
        null=True,
    )
    depends_on = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name=_('Dependent on'),
        help_text=_(
            'This record is maintained automatically for another record. It '
            'should be automatically updated/deleted. Used for PTR records'
            'that depend on A records.'
        )
    )
    auto_ptr = ChoiceField(
        _('Auto PTR record'),
        choices=AutoPtrOptions,
        default=AutoPtrOptions.ALWAYS,
    )

    class Meta:
        db_table = u'records'
        ordering = ('name', 'type')
        unique_together = ('name', 'type', 'content')
        verbose_name = _("record")
        verbose_name_plural = _("records")

    @property
    def opened_requests(self):
        from powerdns.models import RequestStates
        return self.requests.filter(state=RequestStates.OPEN.id).all()

    def request_factory(operation):
        def result(self):
            def fmt(str_, **kwargs):
                return str_.format(
                    obj=type(self)._meta.object_name.lower(),
                    opr=operation,
                    **kwargs
                )

            if (
                get_current_user().has_perm(
                    fmt('powerdns.{opr}_{obj}'), self
                ) and
                can_edit(get_current_user(), self) or
                can_delete(get_current_user(), self)
            ):
                return '<a href={}>{}</a>'.format(
                    reverse(
                        fmt('admin:powerdns_{obj}_{opr}'),
                        args=(self.pk,)
                    ),
                    operation.capitalize()
                )
            if operation == 'delete':
                return '<a href="{}">Request deletion</a>'.format(
                    reverse(
                        fmt('admin:powerdns_deleterequest_add')
                    ) + '?target_id={}&content_type={}'.format(
                        self.pk,
                        ContentType.objects.get_for_model(type(self)).pk,
                    )
                )

            return '<a href="{}">Request change</a>'.format(
                reverse(
                    fmt('admin:powerdns_{obj}request_add')
                ) + '?{}={}'.format(
                    type(self)._meta.object_name.lower(),
                    self.pk
                )
            )
        result.allow_tags = True
        result.__name__ = 'request_' + operation
        return result
    request_change = request_factory('change')
    request_deletion = request_factory('delete')

    def __str__(self):
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

    def force_case(self):
        """Force the name and content case to upper and lower respectively"""
        if self.name:
            self.name = self.name.lower()
        if self.type:
            self.type = self.type.upper()

    def validate_for_conflicts(self):
        """Ensure this record doesn't conflict with other records."""
        def check_unique(comment, **kwargs):
            conflicting = Record.objects.filter(**kwargs)
            if self.pk is not None:
                conflicting = conflicting.exclude(pk=self.pk)
            if conflicting:
                raise ValidationError(comment.format(
                    ', '.join(str(record.id) for record in conflicting)
                ))
        if self.type == 'CNAME':
            check_unique(
                'Cannot create CNAME record. Following conflicting '
                'records exist: {}',
                name=self.name,
            )
        else:
            check_unique(
                'Cannot create a record. Following conflicting CNAME'
                'record exists: {}',
                type='CNAME',
                name=self.name,
            )

    def save(self, *args, **kwargs):
        self.change_date = int(time.time())
        self.ordername = self._generate_ordername()
        if self.type == 'A':
            self.number = IP(self.content).int()
        super(Record, self).save(*args, **kwargs)

    def delete_ptr(self):
        Record.objects.filter(depends_on=self).delete()

    def create_ptr(self):
        """Creates a PTR record for A record creating a domain if necessary."""
        if self.type != 'A':
            raise ValueError(_('Creating PTR only for A records'))
        domain_name, number = to_reverse(self.content)
        if self.auto_ptr == AutoPtrOptions.ALWAYS:
            domain, created = Domain.objects.get_or_create(
                name=domain_name,
                defaults={
                    'template': (
                        self.domain.reverse_template or
                        get_default_reverse_domain()
                    ),
                    'type': self.domain.type,
                }
            )
        elif self.auto_ptr == AutoPtrOptions.ONLY_IF_DOMAIN:
            try:
                domain = Domain.objects.get(name=domain_name)
            except Domain.DoesNotExist:
                return
        else:
            return

        self.delete_ptr()
        Record.objects.create(
            type='PTR',
            domain=domain,
            name='.'.join([number, domain_name]),
            content=self.name,
            depends_on=self,
            owner=self.owner,
            ttl=self.ttl,
            disabled=self.disabled,
        )

    def can_auto_accept(self, user):
        return (
            user.is_superuser or
            user == self.owner or
            user.id in self.authorisations.values_list(
                'authorised', flat=True
            )
        )

    def as_empty_history(self):
        return {
            'content': '',
            'name': '',
            'owner': '',
            'prio': '',
            'remarks': '',
            'ttl':  '',
            'type':  '',
        }

    def as_history_dump(self):
        return {
            'content': self.content or '',
            'name': self.name or '',
            'owner': getattr(self.owner, 'username', ''),
            'prio': self.prio or '',
            'remarks': self.remarks or '',
            'ttl':  self.ttl or '',
            'type':  self.type or '',
        }

rules.add_perm('powerdns.add_record', rules.is_authenticated)
rules.add_perm('powerdns.change_record', rules.is_authenticated)
rules.add_perm('powerdns.delete_record', rules.is_authenticated)


# When we delete a record, the zone changes, but there no change_date is
# updated. We update the SOA record, so the serial changes
@receiver(post_delete, sender=Record, dispatch_uid='record_update_serial')
def update_serial(sender, instance, **kwargs):
    soa = instance.domain.get_soa()
    if soa:
        soa.save()


@receiver(post_save, sender=Record, dispatch_uid='record_create_ptr')
def create_ptr(sender, instance, **kwargs):
    if instance.auto_ptr == AutoPtrOptions.NEVER or instance.type != 'A':
        instance.delete_ptr()
        return
    instance.create_ptr()


class SuperMaster(TimeTrackable):
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

    def __str__(self):
        return self.ip


class DomainMetadata(TimeTrackable):
    domain = models.ForeignKey(Domain, verbose_name=_("domain"))
    kind = models.CharField(_("kind"), max_length=15)
    content = models.TextField(_("content"), blank=True, null=True)

    class Meta:
        db_table = u'domainmetadata'
        ordering = ('domain',)
        verbose_name = _("domain metadata")
        verbose_name_plural = _("domain metadata")

    def __str__(self):
        return str(self.domain)


class CryptoKey(TimeTrackable):
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

    def __str__(self):
        return self.domain
