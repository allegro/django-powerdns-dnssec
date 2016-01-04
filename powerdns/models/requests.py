"""Model for change requests"""

from django.db import models
from django.core.urlresolvers import reverse
from dj.choices import Choices
from dj.choices.fields import ChoiceField
from django.contrib.contenttypes.fields import ContentType, GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from threadlocals.threadlocals import get_current_user
import rules

from powerdns.models import (
    validate_domain_name,
    Owned,
    Domain,
    Record
)
from powerdns.utils import AutoPtrOptions, RecordLike


class RequestStates(Choices):
    _ = Choices.Choice
    OPEN = _('Open')
    ACCEPTED = _('Accepted')
    REJECTED = _('Rejected')


class Request(Owned):
    """Abstract request"""

    class Meta:
        abstract = True

    state = ChoiceField(
        choices=RequestStates,
        default=RequestStates.OPEN,
    )
    key = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    def reject(self):
        """Reject the request"""
        self.state = RequestStates.REJECTED
        self.save()

    def extra_buttons(self):
        perm = 'change_' + self._meta.model_name.lower()
        if get_current_user().has_perm(perm, self):
            yield (reverse(self.view, kwargs={'pk': self.pk}), 'Accept')

    def save(self, *args, **kwargs):
        if self.owner is None:
            self.owner = get_current_user()
        super().save(*args, **kwargs)


class DeleteRequest(Request):
    """A request for object deletion"""
    content_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'target_id')
    view = 'accept_delete'

    def accept(self):
        object_ = self.target
        object_.delete()
        self.state = RequestStates.ACCEPTED
        self.save()

    def __str__(self):
        return 'Delete {}'.format(self.target)


rules.add_perm('powerdns.add_deleterequest', rules.is_authenticated)


class ChangeCreateRequest(Request):
    """Abstract change/create request"""

    ignore_fields = {'owner', 'created', 'modified'}

    class Meta:
        abstract = True

    def accept(self):
        object_ = self.get_object()
        for field_name in type(self).copy_fields:
            if field_name in self.ignore_fields:
                continue
            setattr(object_, field_name, getattr(self, field_name))
        object_.save()
        self.state = RequestStates.ACCEPTED
        self.save()
        return object_


class DomainRequest(ChangeCreateRequest):
    """Request for domain creation/modification"""

    copy_fields = [
        'name',
        'master',
        'type',
        'account',
        'remarks',
        'template',
        'reverse_template',
        'record_auto_ptr'
    ]

    domain = models.ForeignKey(
        Domain,
        related_name='requests',
        null=True,
        blank=True,
        help_text=_(
            'The domain for which a change is requested'
        ),
    )
    parent_domain = models.ForeignKey(
        Domain,
        related_name='child_requests',
        null=True,
        blank=True,
        help_text=_(
            'The parent domain for which a new subdomain is to be created'
        ),

    )
    name = models.CharField(
        _("name"),
        max_length=255,
        validators=[validate_domain_name],
        blank=False,
        null=False,
    )
    master = models.CharField(
        _("master"), max_length=128, blank=True, null=True,
    )
    type = models.CharField(
        _("type"),
        max_length=6,
        blank=True,
        null=True,
        choices=Domain.DOMAIN_TYPE,
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
        related_name='template_for_requests'
    )
    reverse_template = models.ForeignKey(
        'powerdns.DomainTemplate',
        verbose_name=_('Reverse template'),
        blank=True,
        null=True,
        related_name='reverse_template_for_requests',
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

    view = 'accept_domain'

    def __str__(self):
        return self.name

    def get_object(self):
        if self.domain is not None:
            return self.domain
        else:
            return Domain(owner=self.owner)


# rules.add_perm('powerdns', rules.is_authenticated)
rules.add_perm('powerdns.add_domainrequest', rules.is_authenticated)


class RecordRequest(ChangeCreateRequest, RecordLike):

    copy_fields = [
        'domain',
        'name',
        'type',
        'content',
        'prio',
        'ordername',
        'auth',
        'disabled',
        'remarks',
        'ttl',
    ]

    domain = models.ForeignKey(
        Domain,
        related_name='record_requests',
        null=False,
        help_text=_(
            'The domain for which a record is to be added'
        ),
    )
    record = models.ForeignKey(
        Record,
        related_name='requests',
        null=True,
        blank=True,
        help_text=_(
            'The record for which a change is being requested'
        ),
    )
    name = models.CharField(
        _("name"), max_length=255, blank=False, null=False,
        validators=[validate_domain_name],
        help_text=_("Actual name of a record. Must not end in a '.' and be"
                    " fully qualified - it is not relative to the name of the"
                    " domain!"),
    )
    type = models.CharField(
        _("type"), max_length=6, blank=True, null=True,
        choices=Record.RECORD_TYPE, help_text=_("Record qtype"),
    )
    content = models.CharField(
        _("content"), max_length=255, blank=True, null=True,
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
    view = 'accept_record'

    def get_record_pk(self):
        if self.record:
            return self.record.pk

    def __str__(self):
        if self.prio is not None:
            content = "%d %s" % (self.prio, self.content)
        else:
            content = self.content
        return "%s IN %s %s" % (self.name, self.type, content)

    def get_object(self):
        if self.record is not None:
            return self.record
        else:
            return Record(domain=self.domain, owner=self.owner)


rules.add_perm('powerdns.add_recordrequest', rules.is_authenticated)
