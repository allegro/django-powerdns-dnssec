"""Models and signal subscriptions for templating system"""

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from dj.choices.fields import ChoiceField

from powerdns.models.powerdns import Domain, Record
from powerdns.utils import AutoPtrOptions


class DomainTemplateManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class DomainTemplate(models.Model):
    """A predefined template containing several record templates"""

    copy_fields = ['auto_ptr', 'type']

    name = models.CharField(
        _('Template identifier'),
        unique=True,
        max_length=255
    )
    objects = DomainTemplateManager()
    type = models.CharField(
        _("type"), max_length=6, blank=True, null=True,
        choices=Domain.DOMAIN_TYPE, help_text=_("Record type"),
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
    is_public_domain = models.BooleanField(default=True)

    auto_ptr = ChoiceField(
        choices=AutoPtrOptions,
        default=AutoPtrOptions.ALWAYS,
    )

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def add_domain_url(self):
        """Return URL for 'Add domain' action"""
        return (
            reverse('admin-deprecated:powerdns_domain_add') +
            '?template={}'.format(self.pk)
        )

    def add_domain_link(self):
        return '<a href="{}">Create domain</a>'.format(self.add_domain_url())
    add_domain_link.allow_tags = True

    def extra_buttons(self):
        yield (self.add_domain_url(), 'Create domain')


class RecordTemplateManager(models.Manager):
    def get_by_natural_key(self, domain_name, type, name, content):
        return self.get(
            domain_template__name=domain_name,
            type=type,
            name=name,
            content=content,
        )


class RecordTemplate(models.Model):
    """A predefined record template that would cause a corresponding record
    to be created."""
    objects = RecordTemplateManager()
    domain_template = models.ForeignKey(
        DomainTemplate, verbose_name=_('Domain template')
    )
    type = models.CharField(
        _("type"), max_length=6, blank=True, null=True,
        choices=Record.RECORD_TYPE, help_text=_("Record type"),
    )
    name = models.CharField(_('name'), max_length=255)
    content = models.CharField(_('content'), max_length=255)
    ttl = models.PositiveIntegerField(
        _("TTL"), blank=True, null=True, default=3600,
        help_text=_("TTL in seconds"),
    )
    prio = models.PositiveIntegerField(
        _("priority"), blank=True, null=True,
        help_text=_("For MX records, this should be the priority of the"
                    " mail exchanger specified"),
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
    remarks = models.TextField(_('Additional remarks'), blank=True)

    def natural_key(self):
        return (self.domain_template.name, self.type, self.name, self.content)

    def __str__(self):
        if self.prio is not None:
            content = "%d %s" % (self.prio, self.content)
        else:
            content = self.content
        return "%s IN %s %s" % (self.name, self.type, content)

    def get_kwargs(self, domain):
        kwargs = {}
        template_kwargs = {
            'domain-name': domain.name,
        }
        for argname in ['type', 'ttl', 'prio', 'auth']:
            kwargs[argname] = getattr(self, argname)
        for argname in ['name', 'content']:
            kwargs[argname] = getattr(self, argname).format(**template_kwargs)
        kwargs['template'] = self
        kwargs['domain'] = domain
        return kwargs

    def create_record(self, domain):
        """Creates, saves and returns a record for this domain"""
        kwargs = self.get_kwargs(domain)
        record, created = Record.objects.update_or_create(
            type=kwargs['type'], name=kwargs['name'],
            content=kwargs['content'],
            defaults=kwargs,
        )
        return record

    def update_record(self, record):
        kwargs = self.get_kwargs(record.domain)
        for kwarg, value in kwargs.items():
            setattr(record, kwarg, value)


@receiver(
    post_save, sender=Domain, dispatch_uid='domain_update_templated_records'
)
def update_templated_records(sender, instance, **kwargs):
    """Deletes and creates records appropriately to the template"""
    if instance.template is None:
        return
    instance.record_set.exclude(
        template__isnull=True
    ).exclude(
        template__domain_template=instance.template
    ).delete()
    existing_template_ids = set(
        instance.record_set.exclude(
            template__isnull=True
        ).values_list('template__id', flat=True)
    )
    for template in instance.template.recordtemplate_set.exclude(
        pk__in=existing_template_ids,
    ):
        template.create_record(instance)


@receiver(
    post_save,
    sender=RecordTemplate,
    dispatch_uid='record_template_modify_templated_records',
)
def modify_templated_records(sender, instance, created, **kwargs):
    if created:
        for domain in instance.domain_template.domain_set.all():
            instance.create_record(domain)
    else:
        for record in instance.record_set.all():
            instance.update_record(record)
            record.save()
