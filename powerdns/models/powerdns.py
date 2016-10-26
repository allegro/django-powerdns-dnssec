import base64
import hashlib
import ipaddress
import sys
import time

import rules
from dj.choices.fields import ChoiceField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from threadlocals.threadlocals import get_current_user

from powerdns.models import OwnershipByService, OwnershipType
from powerdns.utils import (
    AutoPtrOptions,
    is_authorised,
    is_owner,
    no_object,
    Owned,
    RecordLike,
    TimeTrackable,
    to_reverse,
    reverse_pointer,
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


class PreviousStateMixin(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = [f.name for f in self._meta.get_fields()]
        self._original_values = {
            k: v for k, v in self.__dict__.items() if k in fields
        }

    class Meta:
        abstract = True


def get_ptr_obj(ip, content):
    """Return PTR object for `ip` and `content` or None"""
    ptr = None
    rev_ptr = reverse_pointer(ip)
    try:
        ptr = Record.objects.get(
            type='PTR', name=rev_ptr, content=content,
        )
    except Record.DoesNotExist:
        pass
    return ptr


def get_default_reverse_domain():
    """Returns a default reverse domain."""
    # Avoid circular import (.templates imports this file)
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


class Domain(PreviousStateMixin, OwnershipByService, TimeTrackable, Owned):
    '''
    PowerDNS domains
    '''
    DOMAIN_TYPE = (
        ('MASTER', 'MASTER'),
        ('NATIVE', 'NATIVE'),
        ('SLAVE', 'SLAVE'),
    )
    copy_fields = ['auto_ptr']
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
    auto_ptr = ChoiceField(
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
    direct_owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='DomainOwner',
        related_name='domain_owners'
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

    def can_auto_accept(self, user):
        return (
            user.is_superuser or
            self.unrestricted or
            user == self.owner or
            user.id in self.authorisations.values_list(
                'authorised', flat=True
            ) or self._has_access_by_service(user)
        )

    def as_empty_history(self):
        """We don't care about domain history for now"""
        return {}

    def as_history_dump(self):
        """We don't care about domain history for now"""
        return {}

    @property
    def owners(self):
        """Return queryset of all owners (direct and by service)"""
        return (self.direct_owners.all() | self.service.owners.all())


class DomainOwner(models.Model):
    domain = models.ForeignKey(Domain)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    ownership_type = models.CharField(
        max_length=10, db_index=True,
        choices=[(type_.name, type_.value) for type_ in OwnershipType],
    )


rules.add_perm('powerdns', rules.is_authenticated)
rules.add_perm('powerdns.add_domain', rules.is_superuser)
rules.add_perm('powerdns.change_domain', can_edit)
rules.add_perm('powerdns.delete_domain', can_delete)


class Record(
    PreviousStateMixin, OwnershipByService, TimeTrackable, Owned, RecordLike
):
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
        _("type"), max_length=6, blank=False, null=True,
        choices=RECORD_TYPE, help_text=_("Record qtype"),
    )
    content = models.CharField(
        _("content"), max_length=255, blank=True, null=True,
        help_text=_("The 'right hand side' of a DNS record. For an A"
                    " record, this is the IP address"),
    )
    number = models.DecimalField(
        _("IP number"), null=True, blank=True, default=None, editable=False,
        db_index=True, max_digits=39, decimal_places=0
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
    delete_request = GenericRelation(
        'DeleteRequest',
        content_type_field='content_type',
        object_id_field='target_id',
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
            self.number = int(ipaddress.ip_address(self.content))
        super(Record, self).save(*args, **kwargs)

    def get_ptr(self):
        """Get PTR for `self` record if record is A or AAAA type."""
        if self.type in {'A', 'AAAA'}:
            return get_ptr_obj(self.content, self.name)

    def _delete_old_ptr(self):
        """
        Delete PTR for A/AAAA record when `name` or `content` was updated.

        This fn. works for case where `record.name` or `record.content` has
        changed and record A (or AAAA) is already matched with PTR.
        In such case looking for PTR depending on current record `name` or
        `content` fails (PTR was created for values which are updated now).
        To fix that PTR should be query by values before the update.
        """
        if (
            (
                # delete old PTR, when content or name has changed
                self._original_values['content'] != self.content or
                self._original_values['name'] != self.name
            ) and
            (
                self._original_values['content'] and
                self._original_values['name']
            )
        ):
            old_ptr = get_ptr_obj(
                self._original_values['content'],
                self._original_values['name']
            )
            if old_ptr:
                old_ptr.delete()

    def delete_ptr(self):
        """
        Delete ptr for `self` if exists
        """
        if self.type not in {'A', 'AAAA'}:
            return

        self._delete_old_ptr()
        current_ptr = self.get_ptr()
        if current_ptr:
            current_ptr.delete()

    def create_ptr(self):
        """Creates a PTR record for A record creating a domain if necessary."""
        if self.type != 'A':
            raise ValueError(_('Creating PTR only for A records'))
        domain_name, number = to_reverse(self.content)
        if self.domain.auto_ptr == AutoPtrOptions.ALWAYS:
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
        elif self.domain.auto_ptr == AutoPtrOptions.ONLY_IF_DOMAIN:
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
            ) or self._has_access_by_service(user)
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


def _update_records_ptrs(domain):
    records = Record.objects.filter(domain=domain, type='A')
    for record in records:
        _create_ptr(record)


@receiver(post_save, sender=Domain, dispatch_uid='domain_update_ptr')
def update_ptr(sender, instance, **kwargs):
    if instance._original_values['auto_ptr'] == instance.auto_ptr:
        return
    _update_records_ptrs(instance)


def _create_ptr(record):
    if (
        record.domain.auto_ptr == AutoPtrOptions.NEVER or
        record.type not in {'A', 'AAAA'}
    ):
        record.delete_ptr()
        return
    record.create_ptr()


@receiver(post_save, sender=Record, dispatch_uid='record_create_ptr')
def create_ptr(sender, instance, **kwargs):
    _create_ptr(instance)


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
