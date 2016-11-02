from django.test import TestCase

from threadlocals.threadlocals import set_current_user
from django.contrib.auth import get_user_model

from powerdns.models import (
    Domain,
    DomainRequest,
    Record,
    RecordRequest,
)
from powerdns.tests.utils import (
    ServiceFactory,
    assert_does_exist,
    assert_not_exists,
)


class TestRequests(TestCase):
    """Tests for domain/record requests"""

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            'user1', 'user1@example.com', 'password'
        )
        self.user2 = get_user_model().objects.create_user(
            'user2', 'user2@example.com', 'password'
        )
        self.domain = Domain.objects.create(
            name='example.com',
            type='NATIVE',
            owner=self.user1
        )
        self.record = Record.objects.create(
            domain=self.domain,
            name='forum.example.com',
            type='CNAME',
            content='phpbb.example.com',
            owner=self.user1,
        )

    def test_subdomain_creation(self):
        set_current_user(self.user1)
        request = DomainRequest.objects.create(
            parent_domain=self.domain,
            target_name='subdomain.example.com',
            target_owner=self.user1,
            target_service=ServiceFactory(),
        )
        request.accept()
        assert_does_exist(
            Domain, name='subdomain.example.com', owner=self.user1
        )

    def test_domain_change(self):
        request = DomainRequest.objects.create(
            domain=self.domain,
            target_name='example.com',
            target_type='MASTER',
            owner=self.user2,
            target_owner=self.user1,
            target_service=ServiceFactory(),
        )
        request.accept()
        assert_does_exist(
            Domain,
            name='example.com',
            type='MASTER',
            owner=self.user1
        )
        assert_not_exists(Domain, name='example.com', type='NATIVE')

    def test_record_creation(self):
        request = RecordRequest.objects.create(
            domain=self.domain,
            target_type='CNAME',
            target_name='site.example.com',
            target_content='www.example.com',
            owner=self.user1,
            target_owner=self.user2,
        )
        request.accept()
        assert_does_exist(
            Record,
            content='www.example.com',
            owner=self.user2,
        )

    def test_record_change(self):
        request = RecordRequest.objects.create(
            domain=self.domain,
            record=self.record,
            target_type='CNAME',
            target_name='forum.example.com',
            target_content='djangobb.example.com',
            target_owner=self.user2,
            owner=self.user1,
        )
        request.accept()
        assert_does_exist(Record, content='djangobb.example.com')
        assert_not_exists(Record, content='phpbb.example.com')
