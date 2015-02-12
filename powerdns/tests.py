# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.test import TestCase

from powerdns.models import validate_dns_nodot, validate_ipv6_address


class TestValidators(TestCase):

    def test_validate_dns_nodot(self):
        validate_dns_nodot('some.valid.record.name')
        self.assertRaises(
            ValidationError,
            validate_dns_nodot,
            'some.invalid.record.name.'
        )

    def test_validate_ipv6_address(self):
        validate_ipv6_address('2001:db8::1428:57ab')
        self.assertRaises(
            ValidationError,
            validate_ipv6_address,
            '2001:0db8:0000:0000:0000:0000:1428:zonk'
        )
        self.assertRaises(
            ValidationError,
            validate_ipv6_address,
            '192.168.56.1'
        )
