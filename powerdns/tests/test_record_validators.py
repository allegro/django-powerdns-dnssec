# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.test import TestCase

from powerdns.models import Record, Domain


class TestRecordValidators(TestCase):

    def setUp(self):
        self.domain = Domain(name='example.com')
        self.domain.save()

    def _validate(self, **values):
        values.setdefault('domain', self.domain)
        values.setdefault('change_date', '20150305')
        Record(**values).full_clean()

    def _check_invalid(self, **values):
        with self.assertRaises(ValidationError):
            self._validate(**values)

    def test_valid_a_record(self):
        """A record validates when provided with IPv4 address."""
        self._validate(
            name='site.example.com',
            type='A',
            content='192.168.1.1'
        )

    def test_invalid_a_record(self):
        """A record doesn't validate when provided with IPv6 address."""
        self._check_invalid(
            name='site.example.com',
            type='A',
            content='2001:db8::1428:57ab'
        )

    def test_valid_aaaa_record(self):
        """AAAA record validates when provided with IPv6 address."""
        self._validate(
            name='site.example.com',
            type='AAAA',
            content='2001:db8::1428:57ab'
        )

    def test_invalid_aaaa_record(self):
        """A record doesn't validate when provided with IPv4 address."""
        self._check_invalid(
            name='site.example.com',
            type='AAAA',
            content='192.168.1.1'
        )

    def test_valid_cname_record(self):
        """CNAME record validates with proper domain name"""
        self._validate(
            name='site.example.com',
            type='CNAME',
            content='www.example.com'
        )

    def test_cname_record_trailing_dot(self):
        """CNAME record doesn't validate with trailing dot"""
        self._check_invalid(
            name='site.example.com',
            type='CNAME',
            content='www.example.com.'
        )

    def test_cname_record_comma(self):
        """CNAME record doesn't validate with a comma"""
        self._check_invalid(
            name='site.example.com',
            type='CNAME',
            content='www,example.com.'
        )

    def test_valid_soa_record_dot(self):
        """SOA record validates with proper data (trailing dots)"""

        self._validate(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster.example.com. '
                '201503291 43200 600 1209600 600'
            )
        )

    def test_valid_soa_record_nodot(self):
        """SOA record validates with proper data (no trailing dots)"""

        self._validate(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com hostmaster.example.com '
                '201503291 43200 600 1209600 600'
            )
        )

    def test_soa_record_missing_fields(self):
        """SOA record doesn't validate with missing fields"""

        self._check_invalid(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster.example.com. '
                '201503291 43200 600 1209600'
            )
        )

    def test_soa_record_invalid_domain(self):
        """SOA record doesn't validate with invalid domain"""

        self._check_invalid(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster,example.com. '
                '201503291 43200 600 1209600 600'
            )
        )

    def test_soa_record_invalid_time(self):
        """SOA record doesn't validate with invalid time field"""

        self._check_invalid(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster.example.com. '
                'notanumber 43200 600 1209600 600'
            )
        )
