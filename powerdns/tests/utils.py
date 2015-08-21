"""Utilities for tests"""

import functools as ft

from django.core.exceptions import ValidationError
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework.test import APIClient

from powerdns.models.powerdns import Record, Domain
from powerdns.models.templates import RecordTemplate, DomainTemplate


class DomainFactory(DjangoModelFactory):
    class Meta:
        model = Domain


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = Record


class DomainTemplateFactory(DjangoModelFactory):
    class Meta:
        model = DomainTemplate


class RecordTemplateFactory(DjangoModelFactory):
    class Meta:
        model = RecordTemplate


class RecordTestCase(TestCase):
    """Base class for tests on records."""

    def setUp(self):
        self.domain = DomainFactory(name='example.com', template=None)

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


def user_client(user):
    """Returns client for a given user"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def assert_exists(exists, Model, **kwargs):
    """Check if given object exists or doesn't exist"""
    if Model.objects.filter(**kwargs).exists() != exists:
        raise AssertionError("Object with arguments {} {}!".format(
            kwargs,
            "doesn't exist" if exists else "exists"
        ))

assert_does_exist = ft.partial(assert_exists, True)
assert_not_exists = ft.partial(assert_exists, False)
