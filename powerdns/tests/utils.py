"""Utilities for tests"""

import functools as ft

import factory
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework.test import APIClient

from powerdns.models.powerdns import Record, Domain
from powerdns.models.requests import DeleteRequest, RecordRequest
from powerdns.models.ownership import ServiceOwner, Service
from powerdns.models.templates import RecordTemplate, DomainTemplate
from powerdns.utils import AutoPtrOptions


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: "user_%d" % n)

    @classmethod
    def _generate(cls, create, attrs):
        user = super(UserFactory, cls)._generate(create, attrs)
        user.set_password('password')
        user.save()
        return user


class DomainTemplateFactory(DjangoModelFactory):
    class Meta:
        model = DomainTemplate

    name = factory.Sequence(lambda n: 'name%d' % n)


class RecordTemplateFactory(DjangoModelFactory):
    class Meta:
        model = RecordTemplate


class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service
    name = factory.Sequence(lambda n: 'service%d' % n)
    uid = factory.Sequence(lambda n: 'uid%d' % n)


class ServiceOwnerFactory(DjangoModelFactory):
    class Meta:
        model = ServiceOwner
    service = factory.SubFactory(UserFactory)
    user = factory.SubFactory(UserFactory)


class DomainFactory(DjangoModelFactory):
    class Meta:
        model = Domain

    name = factory.Sequence(lambda n: 'name%d.com' % n)
    service = factory.SubFactory(ServiceFactory)
    auto_ptr = AutoPtrOptions.NEVER


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = Record

    domain = factory.SubFactory(DomainFactory)
    owner = factory.SubFactory(UserFactory)
    service = factory.SubFactory(ServiceFactory)


class RecordRequestFactory(DjangoModelFactory):
    class Meta:
        model = RecordRequest

    record = factory.SubFactory(RecordFactory)
    domain = factory.SubFactory(DomainFactory)
    owner = factory.SubFactory(UserFactory)


class RecordDeleteRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeleteRequest

    content_type = ContentType.objects.get_for_model(Record)
    target = factory.SubFactory(RecordFactory)


class RecordTestCase(TestCase):
    """Base class for tests on records."""

    def setUp(self):
        self.domain = DomainFactory(
            name='example.com',
            template=None,
            reverse_template=DomainTemplateFactory(name='reverse'),
            auto_ptr=AutoPtrOptions.NEVER,
        )

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
