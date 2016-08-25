"""Tests for auto_ptr feature"""

from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

from powerdns.models.powerdns import Domain, Record
from powerdns.tests.utils import (
    DomainFactory,
    DomainTemplateFactory,
    RecordFactory,
    RecordTemplateFactory,
    assert_does_exist,
    assert_not_exists,
)
from powerdns.utils import AutoPtrOptions


class TestAutoPtr(TestCase):
    """Tests for auto_ptr feature"""

    def setUp(self):
        self.user = User.objects.create_superuser(
            'user', 'user1@example.com', 'password'
        )
        self.reverse_template = DomainTemplateFactory(name='reverse')
        self.alt_reverse_template = DomainTemplateFactory(name='reverse 2')
        self.soa_record = RecordTemplateFactory(
            type='SOA',
            name='{domain-name}',
            content=(
                'ns1.{domain-name} hostmaster.{domain-name} '
                '0 43200 600 1209600 600'
            ),
            domain_template=self.reverse_template,
        )
        self.alt_soa_record = RecordTemplateFactory(
            type='SOA',
            name='{domain-name}',
            content=(
                'nameserver1.{domain-name} hostmaster.{domain-name} '
                '0 43200 1200 1209600 1200'
            ),
            domain_template=self.alt_reverse_template,
        )
        self.ptr_domain = DomainFactory(
            name='example.com',
            template=None,
            reverse_template=self.reverse_template,
            type='NATIVE',
            auto_ptr=AutoPtrOptions.ALWAYS,
        )
        self.ptr_if_domain = DomainFactory(
            name='ptr-if-domain.com',
            template=None,
            reverse_template=self.reverse_template,
            type='NATIVE',
            auto_ptr=AutoPtrOptions.ONLY_IF_DOMAIN,
        )
        self.no_ptr_domain = DomainFactory(
            name='no-ptr--domain.com',
            template=None,
            reverse_template=self.reverse_template,
            type='NATIVE',
            auto_ptr=AutoPtrOptions.NEVER,
        )

    def tearDown(self):
        for Model in [Domain, Record, User]:
            Model.objects.all().delete()

    def test_default_ptr_created(self):
        """A PTR record is created for an A record with default template"""
        RecordFactory(
            domain=self.ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
            owner=self.user,
        )
        domain = Domain.objects.get(name='1.168.192.in-addr.arpa')
        self.assertEqual(domain.type, 'NATIVE')
        self.assertTrue(domain.get_soa().content.endswith('600'))
        assert_does_exist(
            Record,
            domain=domain,
            name='1.1.168.192.in-addr.arpa',
            owner=self.user,
        )

    def test_auto_ptr_edit(self):
        """PTR changes when A changes"""
        record = RecordFactory(
            domain=self.ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        record.content = '192.168.1.9'
        record.save()
        domain = Domain.objects.get(name='1.168.192.in-addr.arpa')
        assert_does_exist(
            Record,
            domain=domain,
            name='9.1.168.192.in-addr.arpa',
        )
        assert_not_exists(
            Record,
            domain=domain,
            name='1.1.168.192.in-addr.arpa',
        )

    def test_auto_ptr_fields_get_update_when_record_is_changed(self):
        record = RecordFactory(
            domain=self.ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
            ttl=3600,
        )

        record.content = '192.168.1.9'
        new_ttl = 7200
        record.ttl = new_ttl
        record.disabled = True
        record.save()

        ptr_record = Record.objects.get(
            domain=Domain.objects.get(name='1.168.192.in-addr.arpa'),
            name='9.1.168.192.in-addr.arpa',
        )
        self.assertTrue(record.ttl == ptr_record.ttl == new_ttl)
        self.assertTrue(record.disabled == ptr_record.disabled is True)

    def test_auto_ptr_off(self):
        """PTR is removed when setting auto_ptr to NEVER"""
        RecordFactory(
            domain=self.ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        domain = Domain.objects.get(
            name='1.168.192.in-addr.arpa'
        )

        self.ptr_domain.auto_ptr = AutoPtrOptions.NEVER
        self.ptr_domain.save()

        assert_not_exists(
            Record,
            domain=domain,
            name='1.1.168.192.in-addr.arpa',
        )

    def test_default_ptr_never(self):
        """A PTR record is not created if auto_ptr set to NEVER"""
        domain = DomainFactory(name='1.168.192.in-addr.arpa')
        RecordFactory(
            domain=self.no_ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        assert_not_exists(
            Record,
            domain=domain,
            name='1.1.168.192.in-addr.arpa'
        )

    def test_ptr_domain_exists(self):
        """A PTR record with 'only-if-domain' is created if domain exists"""
        domain = DomainFactory(name='1.168.192.in-addr.arpa')
        RecordFactory(
            domain=self.ptr_if_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        assert_does_exist(
            Record,
            domain=domain,
            name='1.1.168.192.in-addr.arpa'
        )

    def test_ptr_domain_not_exists(self):
        """A PTR record with 'only-if-domain' is created if domain exists"""
        RecordFactory(
            domain=self.ptr_if_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        assert_not_exists(
            Record,
            name='1.1.168.192.in-addr.arpa'
        )

    def test_alt_ptr_created(self):
        """A PTR record is created for an A record with alternative"""
        self.ptr_domain.reverse_template = self.alt_reverse_template
        RecordFactory(
            domain=self.ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        domain = Domain.objects.get(name='1.168.192.in-addr.arpa')
        self.assertTrue(domain.get_soa().content.endswith('1200'))

    def test_ptr_autoremove(self):
        """A PTR record is automatically removed with its A record"""
        a = RecordFactory(
            domain=self.ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        assert_does_exist(Record, name='1.1.168.192.in-addr.arpa', type='PTR')
        a.delete()
        assert_not_exists(Record, name='1.1.168.192.in-addr.arpa', type='PTR')

    @mock.patch('powerdns.models.powerdns._update_records_ptrs')
    def test_update_ptr_signal_is_fired_when_auto_ptr_is_changed(
        self, update_records
    ):
        RecordFactory(
            domain=self.no_ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        self.no_ptr_domain.auto_ptr = AutoPtrOptions.ALWAYS
        saves_counter = update_records.call_count

        self.no_ptr_domain.save()

        self.assertEqual(update_records.call_count, saves_counter + 1)

    @mock.patch('powerdns.models.powerdns._update_records_ptrs')
    def test_update_ptr_signal_is_skipped_when_auto_ptr_is_changed(
        self, update_records
    ):
        RecordFactory(
            domain=self.no_ptr_domain,
            type='A',
            name='site.example.com',
            content='192.168.1.1',
        )
        saves_counter = update_records.call_count

        self.no_ptr_domain.save()

        self.assertEqual(update_records.call_count, saves_counter)
