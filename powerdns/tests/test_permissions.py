"""Tests for permissions"""

import functools as ft

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from powerdns.models.authorisations import Authorisation
from powerdns.utils import AutoPtrOptions

from powerdns.tests.utils import (
    DomainFactory,
    RecordFactory,
    user_client,
)


def get_url(model, obj_):
    return reverse(
        'api:default:' + model + '-detail', kwargs={'pk': obj_.pk}
    )


get_domain_url = ft.partial(get_url, 'domain')
get_record_url = ft.partial(get_url, 'record')


class TestPermissions(TestCase):
    """Test class for permission tests"""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'superuser@example.com', 'password'
        )
        self.user = User.objects.create_user(
            'user', 'superuser@example.com', 'password'
        )
        self.su_domain = DomainFactory(
            name='su.example.com',
            owner=self.superuser,
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.unrestricted_domain = DomainFactory(
            name='unrestricted.example.com',
            owner=self.superuser,
            unrestricted=True,
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.u_domain = DomainFactory(
            name='u.example.com',
            owner=self.user,
            auto_ptr=AutoPtrOptions.NEVER,
        )
        self.su_record = RecordFactory(
            domain=self.su_domain,
            name='www.su.example.com',
            type='A',
            content='192.168.1.1',
            owner=self.superuser,
        )
        self.u_record = RecordFactory(
            domain=self.u_domain,
            name='www.u.example.com',
            type='A',
            content='192.168.1.2',
            owner=self.user,
        )
        self.su_client = user_client(self.superuser)
        self.u_client = user_client(self.user)

    def test_su_can_edit_all_domains(self):
        """Superuser can edit domain not owned by herself."""
        request = self.su_client.patch(
            get_domain_url(self.u_domain),
            {'type': 'NATIVE'},
        )
        self.assertEqual(request.status_code, 200)

    def test_user_cant_edit_other_domains(self):
        """Normal user can't edit domains she doesn't own."""
        request = self.u_client.patch(
            get_domain_url(self.su_domain),
            {'type': 'NATIVE'},
        )
        self.assertEqual(request.status_code, 403)

    def test_authorised_user_can_edit_other_domains(self):
        """Normal user can edit domains she doesn't own if authorised."""
        Authorisation.objects.create(
            owner=self.superuser,
            target=self.su_domain,
            authorised=self.user
        )
        request = self.u_client.patch(
            get_domain_url(self.su_domain),
            {'type': 'NATIVE'},
        )
        self.assertEqual(request.status_code, 200)

    def test_user_can_edit_her_domains(self):
        """Normal user can edit domains she owns."""
        request = self.u_client.patch(
            get_domain_url(self.u_domain),
            {'type': 'NATIVE'},
        )
        self.assertEqual(request.status_code, 200)

    def test_user_can_create_domain(self):
        """Normal user can create domain that is not a child of other domain.
        """
        request = self.u_client.post(
            reverse('api:default:domain-list'),
            {'name': 'example2.com'}
        )
        self.assertEqual(request.status_code, 403)

    def test_user_can_subdomain_her_own(self):
        """Normal user can create domain that is a child of domain she owns."""
        request = self.u_client.post(
            reverse('api:default:domain-list'),
            {'name': 'subdomain.u.example.com'}
        )
        self.assertEqual(request.status_code, 403)

    def test_user_cant_subdomain_others(self):
        """Normal user can't create domain that is a child of not owned domain.
        """
        request = self.u_client.post(
            reverse('api:default:domain-list'),
            {'name': 'subdomain.su.example.com'}
        )
        self.assertEqual(request.status_code, 403)

    def test_su_can_edit_all_records(self):
        """Superuser can edit record not owned by herself."""
        request = self.su_client.patch(
            get_record_url(self.u_record),
            {'content': '192.168.1.3'},
        )
        self.assertEqual(request.status_code, 200)

    def test_u_cant_edit_other_records(self):
        """Normal user can't edit record not owned by herself."""
        request = self.u_client.patch(
            get_record_url(self.su_record),
            {'content': '192.168.1.3'},
        )
        self.assertEqual(request.status_code, 403)

    def test_authorised_user_can_edit_other_records(self):
        """Normal user can edit record not owned by herself if authorised."""
        Authorisation.objects.create(
            owner=self.superuser,
            target=self.su_record,
            authorised=self.user,
        )
        request = self.u_client.patch(
            get_record_url(self.su_record),
            {'content': '192.168.1.3'},
        )
        self.assertEqual(request.status_code, 200)

    def test_u_can_edit_her_records(self):
        """Normal user can edit record not owned by herself."""
        request = self.u_client.patch(
            get_record_url(self.u_record),
            {'content': '192.168.1.3'},
        )
        self.assertEqual(request.status_code, 200)

    def test_su_can_create_records(self):
        """Superuser can create records in domain she doesn't own."""
        request = self.su_client.post(
            reverse('api:default:record-list'),
            {
                'name': 'site.u.example.com',
                'content': '192.168.1.4',
                'type': 'A',
                'domain': get_domain_url(self.u_domain),
            },
        )
        self.assertEqual(request.status_code, 201)

    def test_user_can_create_records_in_her_domain(self):
        """Normal user can create records in domain she owns."""
        request = self.su_client.post(
            reverse('api:default:record-list'),
            {
                'name': 'site.u.example.com',
                'content': '192.168.1.4',
                'type': 'A',
                'domain': get_domain_url(self.u_domain),
            },
        )
        self.assertEqual(request.status_code, 201)

    def test_user_can_create_records_in_unrestricted_domain(self):
        """Normal user can create records in domain that is marked as
        'unrestricted'."""
        request = self.u_client.post(
            reverse('api:default:record-list'),
            {
                'name': 'site.u.example.com',
                'content': '192.168.1.4',
                'type': 'A',
                'domain': get_domain_url(self.unrestricted_domain),
            },
        )
        self.assertEqual(request.status_code, 201)

    def test_user_cant_create_records_in_other_domains(self):
        """Normal user can't create records in domain she doesn't own."""
        request = self.u_client.post(
            reverse('api:default:record-list'),
            {
                'name': 'site.u.example.com',
                'content': '192.168.1.4',
                'type': 'A',
                'domain': get_domain_url(self.su_domain),
            },
        )
        self.assertEqual(request.status_code, 400)
