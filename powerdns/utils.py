"""Utilities for powerdns models"""

from pkg_resources import working_set, Requirement

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dj.choices import Choices


VERSION = working_set.find(Requirement.parse('django-powerdns-dnssec')).version

import rules


# Due to the idiotic way permissions work in admin, we need to give users
# generic 'change' view (so they see the changelist), bo no generic 'delete'
# view (so they can't bulk-delete).

@rules.predicate
def no_object(user, object_):
    return object_ is None


@rules.predicate
def is_owner(user, object_):
    return object_ and object_.owner == user


@rules.predicate
def is_authorised(user, object_):
    return object_ and user in (
        authorisation.authorised
        for authorisation in object_.authorisations.all()
    )


class TimeTrackable(models.Model):
    created = models.DateTimeField(
        verbose_name=_("date created"), auto_now=False, auto_now_add=True,
        editable=False,
    )
    modified = models.DateTimeField(
        verbose_name=_('last modified'), auto_now=True, editable=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_values = {
            k: v for k, v in self.__dict__.items() if not k.startswith('_')
        }

    class Meta:
        abstract = True


class Owned(models.Model):
    """Model that has an owner. This owner is set as default to the creator
    of this model, but can be overridden."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    authorisations = GenericRelation(
        'Authorisation',
        object_id_field='target_id'
    )

    class Meta:
        abstract = True

    def email_owner(self, creator):
        """If the owner is different from the creator - notify the owner."""
        if (
            creator != self.owner and
            settings.ENABLE_OWNER_NOTIFICATIONS and
            hasattr(self.owner, 'email')
        ):
            subject_template, content_template = settings.OWNER_NOTIFICATIONS[
                type(self)._meta.object_name
            ]
            kwargs = {}
            for key, user in [
                ('owner', self.owner),
                ('creator', creator),
            ]:
                kwargs[key + '-email'] = user.email
                kwargs[key + '-name'] = '{} {}'.format(
                    user.first_name,
                    user.last_name
                )
            kwargs['object'] = str(self)

            subject = subject_template.format(**kwargs)
            content = content_template.format(**kwargs)
            send_mail(
                subject,
                content,
                settings.FROM_EMAIL,
                [self.owner.email],
            )


class UserBasedValidator():
    """Generic validator which logic depends on the current user"""

    def set_context(self, field):
        self.user = field.parent.context['request'].user


class PermissionValidator(UserBasedValidator):
    """A validator that only allows objects that user has permission for"""

    def __init__(self, permission, *args, **kwargs):
        self.permission = permission
        super().__init__(*args, **kwargs)

    def __call__(self, object_):
        if not self.user.has_perm(self.permission, object_):
            raise ValidationError("You don't have permission to use this")
        return object_


def to_reverse(ip):
    """
    Given an ip address it will return a tuple of (domain, number)
    suitable for PTR record
    """
    *domain_parts, number = ip.split('.')
    domain = '{}.in-addr.arpa'.format('.'.join(reversed(domain_parts)))
    return (domain, number)


class AutoPtrOptions(Choices):
    _ = Choices.Choice
    NEVER = _("Never")
    ALWAYS = _("Always")
    ONLY_IF_DOMAIN = _("Only if domain exists")


DOMAIN_TYPE = (
    ('MASTER', 'MASTER'),
    ('NATIVE', 'NATIVE'),
    ('SLAVE', 'SLAVE'),
)
