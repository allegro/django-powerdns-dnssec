from django.utils.translation import ugettext_lazy as _
from django.db import models


class TsigKey(models.Model):
    ALGORITHME_TYPE = (
        ('hmac-md5', 'hmac-md5'),
    )
    name = models.CharField(_("name"), max_length=255,
                            blank=False, null=False, help_text=_("Key name"))
    algorithm = models.CharField(_("algorithm"), max_length=50, blank=False,
                                 null=False, choices=ALGORITHME_TYPE)
    secret = models.CharField(_("secret"), max_length=255, blank=False,
                              null=False, help_text=_("Secret key"))

    class Meta:
        db_table = 'tsigkeys'

    def __str__(self):
        return self.name
