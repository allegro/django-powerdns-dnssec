import unittest

from powerdns.models.powerdns import Domain, Record
from powerdns.models.requests import DomainRequest, RecordRequest
from powerdns.tests.utils import assert_does_exist, assert_not_exists


class TestRequests(unittest.TestCase):
    """Tests for domain/record requests"""

    def setUp(self):
        self.domain = Domain.objects.create(
            name='example.com',
            type='NATIVE',
        )
        self.record = Record.objects.create(
            domain=self.domain,
            name='forum.example.com',
            type='CNAME',
            content='phpbb.example.com'

        )

    def tearDown(self):
        for Model in [Domain, DomainRequest, Record, RecordRequest]:
            Model.objects.all().delete()

    def test_subdomain_creation(self):
        request = DomainRequest.objects.create(
            parent_domain=self.domain,
            name='subdomain.example.com'
        )
        request.accept()
        assert_does_exist(Domain, name='subdomain.example.com')

    def test_domain_change(self):
        request = DomainRequest.objects.create(
            domain=self.domain,
            name='example.com',
            type='MASTER',
        )
        request.accept()
        assert_does_exist(Domain, name='example.com', type='MASTER')
        assert_not_exists(Domain, name='example.com', type='NATIVE')

    def test_record_creation(self):
        request = RecordRequest.objects.create(
            domain=self.domain,
            type='CNAME',
            name='site.example.com',
            content='www.example.com',
        )
        request.accept()
        assert_does_exist(Record, content='www.example.com')

    def test_record_change(self):
        request = RecordRequest.objects.create(
            domain=self.domain,
            record=self.record,
            type='CNAME',
            name='forum.example.com',
            content='djangobb.example.com',
        )
        request.accept()
        assert_does_exist(Record, content='djangobb.example.com')
        assert_not_exists(Record, content='phpbb.example.com')
