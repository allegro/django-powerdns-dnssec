"""Tests for record/domain ownership"""

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from powerdns.models import (
    can_auto_accept_record_request,
    Domain,
    Record,
    RecordRequest,
    RequestStates,
)
from powerdns.tests.utils import (
    DomainFactory,
    RecordDeleteRequestFactory,
    RecordFactory,
    ServiceOwnerFactory,
    UserFactory,
    user_client,
)
from powerdns.utils import AutoPtrOptions


class TestOwnershipBase(TestCase):
    """Base test class creating some users."""

    def setUp(self):
        self.user1 = get_user_model().objects.create_superuser(
            'user1', 'user1@example.com', 'password'
        )
        self.user2 = get_user_model().objects.create_superuser(
            'user2', 'user2@example.com', 'password'
        )
        self.client = user_client(self.user1)
        mail.outbox = []

    def tearDown(self):
        for Model in [Domain, Record, get_user_model()]:
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


class TestCreateRecordAccessByServiceOwnership(TestCase):

    def setUp(self):
        self.clicker = UserFactory(username='clicker')
        self.some_dude = UserFactory(username='some_dude')
        self.example_domain = DomainFactory(
            owner=self.clicker,
            name='example.com',
            unrestricted=False,
            auto_ptr=AutoPtrOptions.NEVER,
        )

    def _set_domain_owner(self, domain_owner):
        self.example_domain.owner = domain_owner
        self.example_domain.save()

    def _set_owner(self, domain_ownership):
        self.example_domain.service.owners.clear()
        self.service = ServiceOwnerFactory(
            service=self.example_domain.service, owner=domain_ownership,
        )
        self.service.save()

    def _test_create(self, expected):
        record_request = RecordRequest(
            domain=self.example_domain,
            record=None,
        )
        result = can_auto_accept_record_request(
            record_request, self.clicker, 'create'
        )
        self.assertEqual(result, expected)

    def test_domain_ownership_allows_to_create_new_record_when_blank_auth(
        self
    ):
        self._set_domain_owner(None)
        self._set_owner(self.clicker)
        self._test_create(expected=True)

    def test_domain_ownership_allows_to_create_new_record_when_no_auth(
        self
    ):
        self._set_domain_owner(self.some_dude)
        self._set_owner(self.clicker)
        self._test_create(expected=True)

    def test_no_ownership_when_no_service(
        self
    ):
        self._set_domain_owner(self.some_dude)
        self._set_owner(self.some_dude)
        self.example_domain.service = None
        self.example_domain.save()
        self._test_create(expected=False)

    def test_domain_ownership_rejects_to_create_new_record_when_no_both_perms(
        self
    ):
        self._set_domain_owner(self.some_dude)
        self._set_owner(self.some_dude)
        self._test_create(expected=False)


class TestUpdateRecordAccessByServiceOwnership(TestCase):

    def setUp(self):
        self.clicker = UserFactory(username='clicker')
        self.some_dude = UserFactory(username='some_dude')
        self.example_domain = DomainFactory(
            owner=self.clicker,
            name='example.com',
            unrestricted=False,
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.example_record = RecordFactory(
            owner=None,
            type='A',
            name='example.com',
            content='192.168.1.0',
        )

    def _test_update(self, record_owner, record_ownership, expected):
        self.example_record.owner = record_owner
        self.example_record.service.owners.clear()
        self.service = ServiceOwnerFactory(
            service=self.example_record.service, owner=record_ownership,
        )
        self.example_record.save()
        self.service.save()

        record_request = RecordRequest(
            domain=self.example_domain,
            record=self.example_record,
        )

        result = can_auto_accept_record_request(
            record_request, self.clicker, 'update'
        )
        self.assertEqual(result, expected)

    def test_ownership_allows_update_when_blank_auth(self):
        self._test_update(
            record_owner=None,
            record_ownership=self.clicker,
            expected=True
        )

    def test_ownership_allows_update_when_no_auth(self):
        self._test_update(
            record_owner=self.some_dude,
            record_ownership=self.clicker,
            expected=True
        )

    def test_ownership_rejects_update_when_no_both_perms(self):
        self._test_update(
            record_owner=self.some_dude,
            record_ownership=self.some_dude,
            expected=False
        )


class TestDeleteRecordAccessByServiceOwnership(TestCase):

    def setUp(self):
        self.clicker = UserFactory(username='clicker')
        self.some_dude = UserFactory(username='some_dude')
        self.example_domain = DomainFactory(
            owner=self.clicker,
            name='example.com',
            unrestricted=False,
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.example_record = RecordFactory(
            domain=self.example_domain,
            owner=None,
            type='A',
            name='example.com',
            content='192.168.1.0',
        )

    def _test_delete(self, record_owner, record_ownership, expected):
        self.example_record.owner = record_owner
        self.example_record.service.owners.clear()
        self.service = ServiceOwnerFactory(
            service=self.example_record.service, owner=record_ownership,
        )
        self.example_record.save()
        self.service.save()

        delete_request = RecordDeleteRequestFactory(
            owner=self.clicker,
            target=self.example_record,
            state=RequestStates.OPEN.id,
        )

        result = can_auto_accept_record_request(
            delete_request, self.clicker, 'delete'
        )
        self.assertEqual(result, expected)

    def test_ownership_allows_delete_when_blank_auth(self):
        self._test_delete(
            record_owner=None,
            record_ownership=self.clicker,
            expected=True,
        )

    def test_ownership_allows_delete_when_no_auth(self):
        self._test_delete(
            record_owner=self.some_dude,
            record_ownership=self.clicker,
            expected=True,
        )

    def test_ownership_rejects_delete_when_no_both_perms(self):
        self._test_delete(
            record_owner=self.some_dude,
            record_ownership=self.some_dude,
            expected=False,
        )
