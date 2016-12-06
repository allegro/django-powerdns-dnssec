"""Tests for record/domain ownership"""

from django.test import TestCase

from powerdns.models import OwnershipType
from powerdns.tests.utils import (
    DomainFactory,
    DomainOwnerFactory,
    ServiceFactory,
    ServiceOwnerFactory,
    UserFactory,
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


class TestServiceOwners(TestCase):
    def test_returns_service_owner_when_no_direct_owners(self):
        users = UserFactory.create_batch(2)
        service = ServiceFactory()
        ServiceOwnerFactory(
            service=service,
            owner=users[0],
            ownership_type=OwnershipType.TO.name,
        )
        domain = DomainFactory(service=service)

        service_owners = domain.service_owners

        self.assertCountEqual(
            service_owners.values_list('owner__username', flat=True),
            [users[0].username],
        )

    def test_returns_service_owner_from_correct_domain(self):
        users = UserFactory.create_batch(2)
        service = ServiceFactory()
        ServiceOwnerFactory(
            service=service,
            owner=users[0],
            ownership_type=OwnershipType.TO.name,
        )
        ServiceOwnerFactory(
            service=ServiceFactory(),
            owner=users[1],
            ownership_type=OwnershipType.TO.name,
        )
        domain = DomainFactory(service=service)

        service_owners = domain.service_owners

        self.assertCountEqual(
            service_owners.values_list('owner__username', flat=True),
            [users[0].username],
        )

    def test_returns_direct_owners_when_direct_owners_set(self):
        users = UserFactory.create_batch(2)
        domain = DomainFactory()
        DomainOwnerFactory(
            domain=domain,
            owner=users[0],
            ownership_type=OwnershipType.TO.name,
        )
        DomainOwnerFactory(
            domain=DomainFactory(),
            owner=users[1],
            ownership_type=OwnershipType.TO.name,
        )

        service_owners = domain.service_owners

        self.assertCountEqual(
            service_owners.values_list('owner__username', flat=True),
            [users[0].username],
        )
