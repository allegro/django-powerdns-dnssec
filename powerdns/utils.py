# -*- coding: utf-8 -*-


import sys

from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimeTrackable(models.Model):
    created = models.DateTimeField(
        verbose_name=_("date created"), auto_now=False, auto_now_add=True,
        editable=False,
    )
    modified = models.DateTimeField(
        verbose_name=_('last modified'), auto_now=True, auto_now_add=True,
        editable=False,
    )

    class Meta:
        abstract = True
