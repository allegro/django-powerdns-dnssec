# -*- encoding: utf-8 -*-

from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from powerdns.tests.utils import (
    DomainFactory,
    DomainTemplateFactory,
    RecordFactory,
)
from powerdns.utils import AutoPtrOptions
from powerdns.views import RecordViewSet
from powerdns.models import Domain


class TestApi(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        get_user_model().objects.create_user(
            'user', 'user@test.test', 'user'
        )

        self.client = APIClient()
        self.client.login(username='test', password='test')

        domain = DomainFactory(
            name='example.com', type=None, unrestricted=False,
            record_auto_ptr=2,
            reverse_template=DomainTemplateFactory(name='reverse'),
        )
        for i in range(3):
            RecordFactory(
                type='A', name='example{}.com'.format(i),
                content='192.168.0.{}'.format(i),
                auto_ptr=AutoPtrOptions.ALWAYS,
                domain=domain,

            )
            RecordFactory(
                type='CNAME', name='www.example{}.com'.format(i),
                content='example{}.com'.format(i),
                auto_ptr=AutoPtrOptions.NEVER,
                domain=domain,
            )
            RecordFactory(
                type='TXT', name='example{}.com'.format(i),
                content='Some information{}'.format(i),
                auto_ptr=AutoPtrOptions.NEVER,
                domain=domain,
            )

    def test_record_filters_by_ip_and_type(self):
        request = self.request_factory.get('/')
        request.query_params = QueryDict(
            urlencode([
                ('ip', '192.168.0.1'),
                ('ip', '192.168.0.2'),
                ('type', 'A'),
                ('type', 'CNAME'),
                ('type', 'TXT'),
                ('type', 'PTR'),
            ])
        )

        mvs = RecordViewSet()
        mvs.request = request
        self.assertEqual(len(mvs.get_queryset()), 8)

    def test_no_access_to_not_owned_domain(self):
        url = reverse('domain-list')
        data = {'name': 'allegro.pl'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        domain_id = response.data['id']
        self.assertTrue(Domain.objects.filter(pk=domain_id).exists())

        self.client.login(username='user', password='user')
        data_2 = {'name': 'allegro2.pl'}
        response = self.client.post(url, data_2, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('domain-detail', args=(domain_id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
