from django.test import TestCase

from powerdns.models.powerdns import Domain
from powerdns.tests.utils import (
    DomainFactory,
    DomainTemplateFactory,
    RecordFactory,
    RecordTemplateFactory,
)


class TestAutoPtr(TestCase):
    """Tests for auto_ptr feature"""

    def setUp(self):
        self.reverse_template = DomainTemplateFactory(name='reverse')
        self.alt_reverse_template = DomainTemplateFactory(name='reverse 2')
        self.soa_record = RecordTemplateFactory(
            type='SOA',
            name='{domain-name}',
            content=(
                'ns1.{domain-name} hostmaster.{domain-name} '
                '0 43200 600 1209600 600'
            ),
            domain_template = self.reverse_template,
        )
        self.alt_soar_record = RecordTemplateFactory(
            type='SOA',
            name='{domain-name}',
            content=(
                'nameserver1.{domain-name} hostmaster.{domain-name} '
                '0 43200 1200 1209600 1200'
            ),
            domain_template = self.alt_reverse_template,
        )
        self.domain = DomainFactory(
            name='example.com',
            template=None,
            reverse_template=None,
        )

    def test_default_ptr_created(self):
        """A PTR record is created for an A record with default template"""
        RecordFactory(
            domain=self.domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        domain = Domain.objects.get(name='1.168.192.in-addr.arpa')
        self.assertTrue(domain.get_soa().content.endswith('600'))

    def test_alt_ptr_created(self):
        """A PTR record is created for an A record with alternative"""
        self.domain.reverse_template = self.alt_reverse_template
        RecordFactory(
            domain=self.domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        domain = Domain.objects.get(name='1.168.192.in-addr.arpa')
        self.assertTrue(domain.get_soa().content.endswith('1200'))
