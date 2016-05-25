"""Tests for record/domain ownership"""

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from powerdns.models.powerdns import Domain, Record
from powerdns.tests.utils import DomainFactory, user_client


class TestOwnershipBase(TestCase):
    """Base test class creating some users."""

    def setUp(self):
        self.user1 = User.objects.create_superuser(
            'user1', 'user1@example.com', 'password'
        )
        self.user2 = User.objects.create_superuser(
            'user2', 'user2@example.com', 'password'
        )
        self.client = user_client(self.user1)
        mail.outbox = []

    def tearDown(self):
        for Model in [Domain, Record, User]:
            Model.objects.all().delete()

    def assertOwner(self, request, username, mailed):
        """Assert the owner in returned data is username and he
        was/was not mailed"""
        self.assertEqual(request.data['owner'], username)
        if len(mail.outbox) > 1:
            raise RuntimeError('Tests broken. Clean the outbox on teardown')
        if mailed and len(mail.outbox) == 0:
            raise AssertionError('Notification not sent, while it should be')
        if not mailed and len(mail.outbox) == 1:
            raise AssertionError("Notification sent, while it shouldn't be")


class TestDomainOwnership(TestOwnershipBase):
    """Tests for domain ownership"""

    def test_auto_user(self):
        """Domain owner is set to current user if no owner is specified"""
        request = self.client.post(
            '/api/domains/',
            data={'name': 'owned.example.com'},
        )
        self.assertOwner(request, 'user1', mailed=False)

    def test_explicit_user(self):
        """Domain owner is set to explicitly set value"""
        request = self.client.post(
            '/api/domains/',
            data={'name': 'owned.example.com', 'owner': 'user2'},
        )
        self.assertOwner(request, 'user2', mailed=True)


class TestRecordOwnership(TestOwnershipBase):
    """Tests for record ownership"""

    def setUp(self):
        super(TestRecordOwnership, self).setUp()
        self.domain = DomainFactory(name='owned.example.com')

    def test_auto_user(self):
        """Record owner is set to current user if no owner is specified"""
        request = self.client.post(
            '/api/records/',
            data={
                'domain': '/api/domains/{}/'.format(self.domain.pk),
                'type': 'CNAME',
                'name': 'www.owned.example.com',
                'content': 'blog.owned.example.com',
            },
        )
        self.assertOwner(request, 'user1', mailed=False)

    def test_explicit_user(self):
        """Record owner is set to explicitly set value"""
        request = self.client.post(
            '/api/records/',
            data={
                'domain': '/api/domains/{}/'.format(self.domain.pk),
                'type': 'CNAME',
                'name': 'www.owned.example.com',
                'content': 'blog.owned.example.com',
                'owner': 'user2',
            },
        )
        self.assertOwner(request, 'user2', mailed=True)
