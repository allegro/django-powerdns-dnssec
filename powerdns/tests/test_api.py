# -*- encoding: utf-8 -*-

from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from powerdns.tests.utils import DomainTemplateFactory, RecordFactory
from powerdns.utils import AutoPtrOptions
from powerdns.views import RecordViewSet


class TestApi(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.login(username='test', password='test')

        DomainTemplateFactory(
            name='reverse', type=None, unrestricted=False, record_auto_ptr=2)
        for i in range(3):
            RecordFactory(
                type='A', name='example{}.com'.format(i),
                content='192.168.0.{}'.format(i),
                auto_ptr=AutoPtrOptions.ALWAYS)
            RecordFactory(
                type='CNAME', name='www.example{}.com'.format(i),
                content='example{}.com'.format(i),
                auto_ptr=AutoPtrOptions.NEVER)
            RecordFactory(
                type='TXT', name='example{}.com'.format(i),
                content='Some information{}'.format(i),
                auto_ptr=AutoPtrOptions.NEVER)

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
