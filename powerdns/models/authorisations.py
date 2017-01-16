import rules
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from ..utils import is_owner


class Authorisation(models.Model):
    """A revokable allowance to access / edit domains / records"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        related_name='issued_authorisations',
    )
    authorised = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        related_name='received_authorisations',
    )
    content_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'target_id')

    def __str__(self):
        return '{} authorised {} to {}'.format(
            self.owner,
            self.authorised,
            self.target,
        )


rules.add_perm('powerdns.add_authorisation', rules.is_authenticated)
rules.add_perm(
    'powerdns.change_authorisation', (rules.is_superuser | is_owner)
)
rules.add_perm(
    'powerdns.delete_authorisation', (rules.is_superuser | is_owner)
)
