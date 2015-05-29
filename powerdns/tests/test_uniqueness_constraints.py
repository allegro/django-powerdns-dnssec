"""Tests for keeping uniqueness constraints"""

from powerdns.tests.utils import RecordFactory, RecordTestCase


class TestUniquenessConstraints(RecordTestCase):

    def setUp(self):
        super(TestUniquenessConstraints, self).setUp()
        self.a_record = RecordFactory(
            domain=self.domain,
            type='A',
            name='www.example.com',
            content='192.168.1.1',
        )
        self.cname_record = RecordFactory(
            domain=self.domain,
            type='CNAME',
            name='blog.example.com',
            content='www.example.com',
        )

    def test_nonconflicting_a_record(self):
        """The validation allows an A record when it doesn't conflict with
        existing CNAME"""
        self.validate(type='A', name='wiki.example.com', content='192.168.1.2')

    def test_conflicting_a_record(self):
        """The validation doesn't allow an A recrod when it conflicts with
        existing CNAME"""
        self.check_invalid(
            type='A',
            name='blog.example.com',
            content='192.168.1.2',
        )

    def test_nonconflicting_cname_record(self):
        """The validation allows an CNAME record when it doesn't conflict with
        existing A"""
        self.validate(
            type='CNAME',
            name='wiki.example.com',
            content='site.example.com'
        )

    def test_conflicting_cname_record(self):
        """The validation doesn't allow a CNAME record when it conflicts with
        existing A"""
        self.check_invalid(
            type='CNAME',
            name='www.example.com',
            content='site.example.com'
        )

    def test_conflicting_second_cname_record(self):
        """The validation doesn't allow a CNAME record when it conflicts with
        existing CNAME"""
        self.check_invalid(
            type='CNAME',
            name='blog.example.com',
            content='site.example.com'
        )
