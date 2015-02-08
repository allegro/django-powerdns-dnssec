# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

from django.db import models
from django.utils.translation import ugettext_lazy as _


def python_2_unicode_compatible(klass):
    if sys.version_info[0] == 2:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


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
