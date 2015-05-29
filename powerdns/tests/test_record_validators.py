"""Validation tests"""

from powerdns.tests.utils import RecordTestCase


class TestRecordValidators(RecordTestCase):

    def test_valid_a_record(self):
        """A record validates when provided with IPv4 address."""
        self.validate(
            name='site.example.com',
            type='A',
            content='192.168.1.1'
        )

    def test_invalid_a_record(self):
        """A record doesn't validate when provided with IPv6 address."""
        self.check_invalid(
            name='site.example.com',
            type='A',
            content='2001:db8::1428:57ab'
        )

    def test_valid_aaaa_record(self):
        """AAAA record validates when provided with IPv6 address."""
        self.validate(
            name='site.example.com',
            type='AAAA',
            content='2001:db8::1428:57ab'
        )

    def test_invalid_aaaa_record(self):
        """A record doesn't validate when provided with IPv4 address."""
        self.check_invalid(
            name='site.example.com',
            type='AAAA',
            content='192.168.1.1'
        )

    def test_valid_cname_record(self):
        """CNAME record validates with proper domain name"""
        self.validate(
            name='site.example.com',
            type='CNAME',
            content='www.example.com'
        )

    def test_cname_record_trailing_dot(self):
        """CNAME record doesn't validate with trailing dot"""
        self.check_invalid(
            name='site.example.com',
            type='CNAME',
            content='www.example.com.'
        )

    def test_cname_record_comma(self):
        """CNAME record doesn't validate with a comma"""
        self.check_invalid(
            name='site.example.com',
            type='CNAME',
            content='www,example.com.'
        )

    def test_valid_soa_record_dot(self):
        """SOA record validates with proper data (trailing dots)"""

        self.validate(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster.example.com. '
                '201503291 43200 600 1209600 600'
            )
        )

    def test_valid_soa_record_nodot(self):
        """SOA record validates with proper data (no trailing dots)"""

        self.validate(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com hostmaster.example.com '
                '201503291 43200 600 1209600 600'
            )
        )

    def test_soa_record_missing_fields(self):
        """SOA record doesn't validate with missing fields"""

        self.check_invalid(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster.example.com. '
                '201503291 43200 600 1209600'
            )
        )

    def test_soa_record_invalid_domain(self):
        """SOA record doesn't validate with invalid domain"""

        self.check_invalid(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster,example.com. '
                '201503291 43200 600 1209600 600'
            )
        )

    def test_soa_record_invalid_time(self):
        """SOA record doesn't validate with invalid time field"""

        self.check_invalid(
            name='site.example.com',
            type='SOA',
            content=(
                'example.com. hostmaster.example.com. '
                'notanumber 43200 600 1209600 600'
            )
        )
