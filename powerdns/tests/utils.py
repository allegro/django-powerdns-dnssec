# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.test import TestCase
from factory.django import DjangoModelFactory

from powerdns.models import Record, Domain


class DomainFactory(DjangoModelFactory):
    class Meta:
        model = Domain


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = Record


class RecordTestCase(TestCase):
    """Base class for tests on records."""

    def setUp(self):
        self.domain = DomainFactory(name='example.com')

    def validate(self, **values):
        """
        Perform a full clean of a record with given values"""
        values.setdefault('domain', self.domain)
        values.setdefault('change_date', '20150305')
        Record(**values).full_clean()

    def check_invalid(self, **values):
        """
        Perform a full clean of a record with given values expecting it to fail
        """
        with self.assertRaises(ValidationError):
            self.validate(**values)
