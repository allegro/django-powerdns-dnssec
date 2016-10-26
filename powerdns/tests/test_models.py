"""Tests for record/domain ownership"""

from django.test import TestCase

from powerdns.tests.utils import (
    DomainOwnerFactory,
    ServiceOwnerFactory,
)


class TestDomain(TestCase):

    def test_domain_return_owners_from_service_and_domain(self):
        domain_owner = DomainOwnerFactory()
        service_owner = ServiceOwnerFactory()
        domain_owner.domain.service = service_owner.service

        self.assertEqual(domain_owner.domain.owners.count(), 2)
        domain_users = domain_owner.domain.owners.values_list(
            'username', flat=True,
        )
        self.assertTrue(
            domain_owner.owner.username in domain_users and
            service_owner.owner.username in domain_users
        )
