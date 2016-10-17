"""Tests for keeping uniqueness constraints for requests"""

# This file is essentially a 1:1 copy of test_uniqueness_constraints
# The record requests should be validated like records
from django.contrib.auth import get_user_model

from powerdns.models import Domain, Record, RecordRequest
from powerdns.tests.utils import RecordFactory, RecordTestCase


class TestRequestUniquenessConstraints(RecordTestCase):

    def setUp(self):
        super(TestRequestUniquenessConstraints, self).setUp()
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
        self.user = get_user_model().objects.create_user(
            'user1', 'user1@example.com', 'password'
        )

    def tearDown(self):
        for Model in [Domain, Record, get_user_model()]:
            Model.objects.all().delete()

    def validate(self, **values):
        """
        Perform a full clean of a record with given values"""
        values.setdefault('domain', self.domain)
        RecordRequest(**values).full_clean()

    def test_nonconflicting_a_record(self):
        """The validation allows an A record when it doesn't conflict with
        existing CNAME"""
        self.validate(
            target_type='A',
            target_name='wiki.example.com',
            target_content='192.168.1.2',
            target_owner=self.user,
        )

    def test_noconflict_with_itself(self):
        """A CNAME record can be resaved (it doesn't conflict with itself.)"""
        self.validate(
            record=self.cname_record,
            target_type='CNAME',
            target_name='blog.example.com',
            target_content='www2.example.com',
            target_owner=self.user,
        )

    def test_conflicting_a_record(self):
        """The validation doesn't allow an A recrod when it conflicts with
        existing CNAME"""
        self.check_invalid(
            target_type='A',
            target_name='blog.example.com',
            target_content='192.168.1.2',
            target_owner=self.user,
        )

    def test_nonconflicting_cname_record(self):
        """The validation allows an CNAME record when it doesn't conflict with
        existing A"""
        self.validate(
            target_type='CNAME',
            target_name='wiki.example.com',
            target_content='site.example.com',
            target_owner=self.user,
        )

    def test_conflicting_cname_record(self):
        """The validation doesn't allow a CNAME record when it conflicts with
        existing A"""
        self.check_invalid(
            target_type='CNAME',
            target_name='www.example.com',
            target_content='site.example.com',
            target_owner=self.user,
        )

    def test_conflicting_second_cname_record(self):
        """The validation doesn't allow a CNAME record when it conflicts with
        existing CNAME"""
        self.check_invalid(
            target_type='CNAME',
            target_name='blog.example.com',
            target_content='site.example.com',
            target_owner=self.user,
        )
