# -*- encoding: utf-8 -*-
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from powerdns.models.powerdns import Record
from powerdns.models.requests import (
    DeleteRequest,
    RecordRequest,
    RequestStates,
)
from powerdns.tests.utils import (
    DomainFactory,
    DomainTemplateFactory,
    RecordFactory,
    RecordRequestFactory,
    UserFactory
)
from powerdns.utils import AutoPtrOptions
from dnsaas.api.v2.views import RecordViewSet


class TestApi(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        get_user_model().objects.create_superuser(
            'superuser', 'superuser@test.test', 'superuser'
        )
        get_user_model().objects.create_user(
            'user', 'user@test.test', 'user'
        )

        self.client = APIClient()
        self.client.login(username='user', password='user')

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


class BaseApiTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        self.super_user = get_user_model().objects.create_superuser(
            'super_user', 'test@test.test', 'super_user'
        )
        self.client = APIClient()


class TestRecords(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.regular_user1 = get_user_model().objects.create_user(
            'regular_user1', 'regular_user1@test.test', 'regular_user1'
        )
        self.regular_user2 = get_user_model().objects.create_user(
            'regular_user2', 'regular_user2@test.test', 'regular_user2'
        )

    def test_record_is_created_when_superuser(self):
        self.client.login(username='super_user', password='super_user')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'cname'.upper(),
            'domain': domain.id,
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_record_is_created_when_user_owns_domain(self):
        self.client.login(username='regular_user1', password='regular_user1')
        domain = DomainFactory(name='example.com', owner=self.regular_user1)
        data = {
            'type': 'cname'.upper(),
            'domain': domain.id,
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_record_is_not_created_when_domain_is_not_owned(self):
        self.client.login(username='regular_user1', password='regular_user1')
        domain = DomainFactory(name='example.com', owner=self.regular_user2)
        data = {
            'type': 'cname'.upper(),
            'domain': domain.id,
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_validation_ip_address_if_domain_is_public(self):
        domain = DomainFactory(
            name='example2.com', owner=self.regular_user2,
            template=DomainTemplateFactory(
                is_public_domain=True, name="Public"
            )
        )
        self.client.login(username='regular_user1', password='regular_user1')

        data = {
            'type': 'A',
            'domain': domain.id,
            'name': 'example2.com',
            'content': '10.0.0.0',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['content'], ['IP address cannot be private.']
        )

    def test_user_is_set_correct_when_adding_record_with_owner(self):
        self.client.login(username='super_user', password='super_user')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'cname'.upper(),
            'domain': domain.id,
            'name': 'example.com',
            'content': '192.168.0.1',
            'owner': self.regular_user1.username,
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.regular_user1.username)
        record_request = RecordRequest.objects.get(
            record__id=response.data['id'],
        )
        self.assertEqual(record_request.owner, self.super_user)
        self.assertEqual(record_request.target_owner, self.regular_user1)

    def test_user_is_set_correct_when_adding_record_without_owner(self):
        self.client.login(username='super_user', password='super_user')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'cname'.upper(),
            'domain': domain.id,
            'name': 'example.com',
            'content': '192.168.0.1',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.super_user.username)
        record_request = RecordRequest.objects.get(
            record__id=response.data['id'],
        )
        self.assertEqual(record_request.owner, self.super_user)
        self.assertEqual(record_request.target_owner, self.super_user)

    #
    # updates
    #
    def test_update_record_when_recordrequest_doesnt_exist(self):
        self.client.login(username='super_user', password='super_user')
        record = RecordFactory(
            auto_ptr=AutoPtrOptions.NEVER.id,
            type='A',
            name='blog.com',
            content='192.168.1.0',
        )
        new_name = 'new-' + record.name
        response = self.client.patch(
            reverse('api:v2:record-detail', kwargs={'pk': record.pk}),
            data={'name': new_name},
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.name, new_name)
        self.assertEqual(
            RecordRequest.objects.filter(record__id=record.id).count(), 1
        )

    def test_update_record_when_cant_auto_accept(self):
        self.client.login(username='regular_user1', password='regular_user1')
        record_request = RecordRequestFactory(
            state=RequestStates.ACCEPTED.id,
            record__auto_ptr=AutoPtrOptions.NEVER.id,
            record__type='A',
            record__name='blog.com',
            record__content='192.168.1.0',
        )
        new_name = 'new-' + record_request.record.name
        response = self.client.patch(
            reverse(
                'api:v2:record-detail',
                kwargs={'pk': record_request.record.pk},
            ),
            data={'name': new_name},
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        record_request.record.refresh_from_db()
        self.assertFalse('new' in record_request.record.name)
        self.assertEqual(
            RecordRequest.objects.filter(
                record__id=record_request.record.id
            ).count(),
            2,
        )

    def test_reject_update_when_request_already_exists(self):
        self.client.login(username='regular_user1', password='regular_user1')
        record_request = RecordRequestFactory(
            state=RequestStates.OPEN.id,
            record__auto_ptr=AutoPtrOptions.NEVER.id,
            record__type='A',
            record__name='blog.com',
            record__content='192.168.1.0',
        )
        new_name = 'new-' + record_request.record.name
        response = self.client.patch(
            reverse(
                'api:v2:record-detail',
                kwargs={'pk': record_request.record.pk},
            ),
            data={'name': new_name},
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(
            response.status_code, status.HTTP_412_PRECONDITION_FAILED,
        )
        self.assertEqual(
            response.data['record_request_ids'][0], record_request.id
        )

    def test_allow_update_when_request_already_exists_but_superuser(
        self
    ):
        self.client.login(username='super_user', password='super_user')
        record_request = RecordRequestFactory(
            state=RequestStates.OPEN.id,
            record__auto_ptr=AutoPtrOptions.NEVER.id,
            record__type='A',
            record__name='blog.com',
            record__content='192.168.1.0',
        )
        new_name = 'new-' + record_request.record.name
        response = self.client.patch(
            reverse(
                'api:v2:record-detail',
                kwargs={'pk': record_request.record.pk},
            ),
            data={'name': new_name},
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record_request.record.refresh_from_db()
        self.assertEqual(record_request.record.name, new_name)
        self.assertEqual(
            RecordRequest.objects.filter(
                record__id=record_request.record.id
            ).count(),
            2,
        )

    def test_user_is_set_correct_when_updating_record_with_owner(self):
        self.client.login(username='super_user', password='super_user')
        record = RecordFactory(
            auto_ptr=AutoPtrOptions.NEVER.id,
            type='A',
            name='blog.com',
            content='192.168.1.0',
            owner=self.regular_user1,
        )
        new_name = 'new-' + record.name
        response = self.client.patch(
            reverse('api:v2:record-detail', kwargs={'pk': record.pk}),
            data={
                'name': new_name,
                'owner': self.regular_user2.username,
            },
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.owner, self.regular_user2)
        record_request = RecordRequest.objects.get(record__id=record.id)
        self.assertEqual(record_request.owner, self.super_user)
        self.assertEqual(record_request.target_owner, self.regular_user2)

    def test_user_is_set_correct_when_updating_record_without_owner(self):
        self.client.login(username='super_user', password='super_user')
        record = RecordFactory(
            auto_ptr=AutoPtrOptions.NEVER.id,
            type='A',
            name='blog.com',
            content='192.168.1.0',
            owner=self.regular_user1,
        )
        new_name = 'new-' + record.name
        response = self.client.patch(
            reverse('api:v2:record-detail', kwargs={'pk': record.pk}),
            data={'name': new_name},
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.owner, self.regular_user1)
        record_request = RecordRequest.objects.get(record__id=record.id)
        self.assertEqual(record_request.owner, self.super_user)
        self.assertEqual(record_request.target_owner, None)

    def test_owner_keeps_value_when_no_owner_in_update(self):
        """
        1. Create record r1 with owner o1
        2. Create record request (rr1) for r1 without owner
        3. r1 gets update on owner to o2 while acceptation is pending
        4. rr1 gets acceptation
        5. r1.owner == o2
        """
        self.client.login(username='regular_user1', password='regular_user1')
        record = RecordFactory(
            auto_ptr=AutoPtrOptions.NEVER.id,
            type='A',
            name='blog.com',
            remarks='initial remarks',
            content='192.168.1.0',
            owner=self.super_user,
        )
        response = self.client.patch(
            reverse('api:v2:record-detail', kwargs={'pk': record.pk}),
            data={'remarks': 'updated remarks'},
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        record.owner = self.regular_user2
        record.save()
        RecordRequest.objects.get(record=record).accept()
        record.refresh_from_db()
        self.assertEqual(record.owner, self.regular_user2)
        self.assertEqual(record.remarks, 'updated remarks')

    #
    # deletion
    #
    def test_superuser_deletes_records_with_opened_request(self):
        """Superuser can delete record with OPENED record-requests"""
        self.client.login(username='super_user', password='super_user')
        record_request = RecordRequestFactory(
            state=RequestStates.OPEN.id,
            record__auto_ptr=AutoPtrOptions.NEVER.id,
            record__type='A',
            record__name='blog.com',
            record__content='192.168.1.0',
        )
        response = self.client.delete(
            reverse(
                'api:v2:record-detail',
                kwargs={'pk': record_request.record.pk},
            ),
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # record_request.refresh_from_db doesn't refresh since
        # record_request.record is on_delete=models.DO_NOTHING, so get record
        # by query
        self.assertEqual(
            RecordRequest.objects.get(pk=record_request.id).record_id,
            record_request.record_id,
        )
        with self.assertRaises(Record.DoesNotExist):
            RecordRequest.objects.get(pk=record_request.id).record
        self.assertTrue(
            DeleteRequest.objects.get(target_id=record_request.record_id)
        )

    def test_user_cant_delete_record(self):
        """Regular user can't delete record"""
        self.client.login(username='regular_user1', password='regular_user1')
        record_request = RecordRequestFactory(
            state=RequestStates.ACCEPTED.id,
            record__auto_ptr=AutoPtrOptions.NEVER.id,
            record__type='A',
            record__name='blog.com',
            record__content='192.168.1.0',
        )
        response = self.client.delete(
            reverse(
                'api:v2:record-detail',
                kwargs={'pk': record_request.record.pk},
            ),
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(Record.objects.get(id=record_request.record.id))
        self.assertEqual(
            DeleteRequest.objects.filter(
                target_id=record_request.record.id
            ).count(),
            1,
        )

    def test_user_cant_delete_record_with_opened_request(self):
        """Regular user can't delete record when OPENED record-request
        exists"""
        self.client.login(username='regular_user1', password='regular_user1')
        record_request = RecordRequestFactory(
            state=RequestStates.OPEN.id,
            record__auto_ptr=AutoPtrOptions.NEVER.id,
            record__type='A',
            record__name='blog.com',
            record__content='192.168.1.0',
        )
        response = self.client.delete(
            reverse(
                'api:v2:record-detail',
                kwargs={'pk': record_request.record.pk},
            ),
            format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(
            response.status_code, status.HTTP_412_PRECONDITION_FAILED,
        )
        self.assertTrue(Record.objects.get(id=record_request.record.id))
        self.assertEqual(
            DeleteRequest.objects.filter(
                target_id=record_request.record.id
            ).count(),
            0,
        )


class TestRecordValidation(BaseApiTestCase):
    def test_validation_error_when_A_record_name_is_bad(self):
        self.client.login(username='super_user', password='super_user')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'A',
            'domain': domain.id,
            'name': 'this-is-bad-bad-value-for-name',
            'content': 'this-is-bad-bad-value-for-content',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['name'])

    def test_validation_error_when_A_record_content_is_bad(self):
        self.client.login(username='super_user', password='super_user')
        domain = DomainFactory(name='example.com', owner=self.super_user)
        data = {
            'type': 'A',
            'domain': domain.id,
            'name': 'www.' + domain.name,
            'content': 'ThisIsBadBadValueForContent',
        }
        response = self.client.post(
            reverse('api:v2:record-list'), data, format='json',
            **{'HTTP_ACCEPT': 'application/json; version=v2'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['content'])


class TestObtainAuthToken(TestCase):

    def setUp(self):  # noqa
        self.client = APIClient()  # do not login
        self.user = UserFactory()

    def test_should_return_token_when_correct_credentials_were_sent(self):
        response = self.client.post(
            reverse('get-api-token'),
            {'username': self.user.username, 'password': 'password'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['token'],
            str(self.user.auth_token),
        )

    def test_should_return_400_when_incorrect_credentials_were_sent(self):
        response = self.client.post(
            reverse('get-api-token'),
            {'username': self.user.username, 'password': 'bad-password'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
