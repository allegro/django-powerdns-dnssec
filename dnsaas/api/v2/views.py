
"""Views and viewsets for DNSaaS API"""
import django_filters
import ipaddress
import logging

from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Prefetch, Q

from powerdns.utils import hostname2domain
from powerdns.models import (
    RECORD_A_TYPES,
    CryptoKey,
    DeleteRequest,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordRequest,
    RecordTemplate,
    RequestStates,
    Service,
    SuperMaster,
    TsigKey,
    can_auto_accept_record_request,
)
from rest_framework import filters, serializers, status
from rest_framework.permissions import DjangoObjectPermissions, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView

from .serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordRequestSerializer,
    RecordSerializer,
    RecordTemplateSerializer,
    ServiceSerializer,
    SuperMasterSerializer,
    TsigKeysTemplateSerializer,
)
from powerdns.utils import reverse_pointer


log = logging.getLogger(__name__)


class DomainPermission(DjangoObjectPermissions):

    def has_permission(self, request, view):
        if request.method == 'POST' and not request.user.is_superuser:
            return False
        return super().has_permission(request, view)


class FiltersMixin(object):

    filter_backends = (filters.DjangoFilterBackend,)


class OwnerViewSet(FiltersMixin, ModelViewSet):
    """Base view for objects with owner"""

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.validated_data.get('owner') is None:
            serializer.save(owner=self.request.user)
        else:
            object_ = serializer.save()
            object_.email_owner(self.request.user)


class DomainFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='name', lookup_type='icontains')

    class Meta:
        model = Domain
        fields = ['name', 'owner', 'type']


class DomainViewSet(OwnerViewSet):

    queryset = Domain.objects.all().select_related('owner')
    serializer_class = DomainSerializer
    permission_classes = (DomainPermission,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    filter_class = DomainFilter
    search_fields = ['name', 'owner__username']


class ServiceViewSet(FiltersMixin, ModelViewSet):

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name', 'uid', 'is_active']


class RecordRequestsViewSet(FiltersMixin, ReadOnlyModelViewSet):
    queryset = RecordRequest.objects.all().select_related(
        'owner', 'domain', 'record', 'target_owner',
    ).order_by('-id')
    filter_fields = ('owner', 'state')
    serializer_class = RecordRequestSerializer


class RecordFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(
        name='content', lookup_type='icontains'
    )
    name = django_filters.CharFilter(
        name='name', lookup_type='icontains'
    )

    class Meta:
        model = Record
        fields = ['name', 'content', 'domain', 'owner']


class RecordViewSet(OwnerViewSet):

    queryset = Record.objects.all().select_related(
        'owner', 'domain'
    ).prefetch_related(
        Prefetch(
            "requests",
            queryset=RecordRequest.objects.filter(state=RequestStates.OPEN)
        ),
        Prefetch(
            "delete_request",
            queryset=DeleteRequest.objects.filter(state=RequestStates.OPEN)
        )
    ).order_by('-id')
    serializer_class = RecordSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    filter_class = RecordFilter
    search_fields = [
        'name', 'content', 'type', 'domain__name', 'owner__username'
    ]

    def _set_owner(self, data):
        if 'owner' not in data:
            data['owner'] = self.request.user.username
        return data

    def _custom_clean(self, instance):
        # this would be called by `perform_update` or `perform_create`
        # but since we have `target_` attribute we call it in `create` or
        # `update`
        try:
            instance.clean()
        except ValidationError as e:
            return Response(
                {"error": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
                headers={}
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self._set_owner(request.data.copy())
        )
        serializer.is_valid(raise_exception=True)

        record_request = RecordRequest()
        record_request.copy_records_data(serializer.validated_data.items())
        record_request.owner = request.user
        record_request.target_owner = serializer.validated_data['owner']
        respone_with_error = self._custom_clean(record_request)
        if respone_with_error:
            return respone_with_error

        if can_auto_accept_record_request(
            record_request, request.user, 'create',
        ):
            serializer.instance = record_request.accept()
            data = serializer.data
            code = status.HTTP_201_CREATED
            headers = {}
        else:
            record_request.save()
            data = {
                'record_request_id': record_request.id,
            }
            code = status.HTTP_202_ACCEPTED
            headers = {
                'Location': reverse(
                    'api:v2:recordrequest-detail',
                    kwargs={'pk': record_request.id},
                )
            }
        return Response(data, status=code, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        if (
            serializer.instance.opened_requests and
            not request.user.is_superuser
        ):
            return Response(
                {'record_request_ids':
                    serializer.instance.opened_requests.values_list(
                        'id', flat=True
                    )
                 },
                status=status.HTTP_412_PRECONDITION_FAILED,
                headers={},
            )

        record_request = RecordRequest()
        # in validated_data lands fields required by model, even if they
        # weren't changed, so filter it by matching validated vs initial
        data_to_copy = [
            (field_name, serializer.validated_data[field_name])
            for field_name in (
                serializer.validated_data.keys() &
                serializer.initial_data.keys()
            )
        ]
        record_request.copy_records_data(data_to_copy)
        record_request.domain = serializer.instance.domain
        record_request.owner = request.user
        record_request.target_owner = serializer.validated_data.get('owner')
        record_request.record = serializer.instance
        respone_with_error = self._custom_clean(record_request)
        if respone_with_error:
            return respone_with_error

        if can_auto_accept_record_request(
            record_request, request.user, 'update',
        ):
            serializer.instance = record_request.accept()
            data = serializer.data
            code = status.HTTP_200_OK
            headers = {}
        else:
            record_request.save()
            data = {
                'record_request_id': record_request.id,
            }
            code = status.HTTP_202_ACCEPTED
            headers = {
                'Location': reverse(
                    'api:v2:recordrequest-detail',
                    kwargs={'pk': record_request.id},
                )
            }
        return Response(data, status=code, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.has_owner():
            raise serializers.ValidationError({
                'owner': [
                    'Record requires owner to be deletable. Please contact DNS support.'  # noqa
                ]
            })

        if (
            instance.opened_requests and
            not request.user.is_superuser
        ):
            return Response(
                {'record_request_ids':
                    instance.opened_requests.values_list(
                        'id', flat=True
                    )
                 },
                status=status.HTTP_412_PRECONDITION_FAILED,
                headers={},
            )

        delete_request = DeleteRequest(
            owner=request.user, target=instance,
        )
        if can_auto_accept_record_request(
            delete_request, request.user, 'delete',
        ):
            delete_request.accept()
            code = status.HTTP_204_NO_CONTENT
        else:
            delete_request.save()
            code = status.HTTP_202_ACCEPTED
        return Response(status=code)

    def get_queryset(self):
        queryset = super().get_queryset()
        ips = self.request.query_params.getlist('ip')
        if ips:
            a_records = Record.objects.filter(
                content__in=ips, type__in=RECORD_A_TYPES,
            )
            ptrs = [
                reverse_pointer(r.content) for r in a_records
            ]
            queryset = queryset.filter(
                (Q(content__in=[r.content for r in a_records]) & Q(type__in=RECORD_A_TYPES)) |  # noqa
                (Q(content__in=[r.name for r in a_records]) & Q(type='CNAME')) |  # noqa
                (Q(name__in=[r.name for r in a_records]) & Q(type='TXT')) |
                (Q(name__in=ptrs) & Q(type='PTR'))
            )
        types = self.request.query_params.getlist('type')
        if types:
            queryset = queryset.filter(type__in=types)
        return queryset


class CryptoKeyViewSet(FiltersMixin, ModelViewSet):

    queryset = CryptoKey.objects.all()
    serializer_class = CryptoKeySerializer
    filter_fields = ('domain',)


class DomainMetadataViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainMetadata.objects.all()
    serializer_class = DomainMetadataSerializer
    filter_fields = ('domain',)


class SuperMasterViewSet(FiltersMixin, ModelViewSet):

    queryset = SuperMaster.objects.all()
    serializer_class = SuperMasterSerializer
    filter_fields = ('ip', 'nameserver')


class DomainTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainTemplate.objects.all()
    serializer_class = DomainTemplateSerializer
    filter_fields = ('name',)


class RecordTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = RecordTemplate.objects.all()
    serializer_class = RecordTemplateSerializer
    filter_fields = ('domain_template', 'name', 'content')


class TsigKeysViewSet(FiltersMixin, ModelViewSet):

    queryset = TsigKey.objects.all()
    serializer_class = TsigKeysTemplateSerializer
    filter_fields = ('name', 'secret')


class IPRecordView(APIView):
    """Dedicated view for add/update/delete"""
    permission_classes = (IsAdminUser,)

    @staticmethod
    def _validate_data(data):
        if 'action' not in data:
            return False
        if (
            data['action'] == 'delete' and
            'address' not in data and
            'hostname' not in data
        ):
            return False
        if data['action'] == 'add' and data['new'] != data['old']:
            return False
        if data['action'] == 'add' and not data['old']['hostname']:
            return False
        return True

    def _get_record(self, ip, hostname):
        ip = int(ipaddress.ip_address(ip))
        try:
            record = Record.objects.get(
                type__in=RECORD_A_TYPES, number=ip, name=hostname
            )
        except (Record.DoesNotExist, MultipleObjectsReturned):
            record = None
        return record

    def _add_record(self, data):
        new = data['new']
        try:
            Record.objects.create(
                type='A',
                name=new['hostname'],
                domain=hostname2domain(new['hostname']),
                number=int(ipaddress.ip_address(new['address'])),
                content=new['address']
            )
        except IntegrityError as e:
            return status.HTTP_409_CONFLICT, str(e)
        else:
            return status.HTTP_200_OK, 'created'

    def _update_record(self, data):
        new = data['new']
        old = data['old']
        record = self._get_record(old['address'], old['hostname'])
        if not record:
            return self._add_record(data)

        if new['hostname'] is None and record:
            return self._delete_record(dict(
                address=old['address'], hostname=old['hostname']
            ))
        if record:
            record.name = new['hostname']
            record.domain = hostname2domain(new['hostname'])
            record.content = new['address']
            record.save()
            # If change hostname update name records txt.
            log.info('Update TXT records from: {} hostname to: {}'.format(
                old['hostname'], new['hostname']
            ))
            Record.objects.filter(
                name=old['hostname'],
                type='TXT'
            ).update(
                name=new['hostname'],
                domain=record.domain
            )

        return status.HTTP_200_OK, 'updated'

    def _delete_record(self, data):
        ip, hostname = data['address'], data['hostname']
        record = self._get_record(ip, hostname)
        if record:
            log.warning('Delete record: {}'.format(record))
            record.delete()
            log.warning('Delete TXT records for {} hostname'.format(hostname))
            Record.objects.filter(name=hostname, type='TXT').delete()
            return status.HTTP_200_OK, 'deleted'
        return status.HTTP_200_OK, 'noop'

    def post(self, request):
        data = request.data
        action = data.get('action', None)
        action_mapper = {
            'add': self._add_record,
            'update': self._update_record,
            'delete': self._delete_record,
        }
        if not self._validate_data(data) or action not in action_mapper:
            return Response(
                data={'status': 'Invalid request data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        action_func = action_mapper[action]
        status_code, status_text = action_func(data=data)
        return Response(
            data={'status': status_text},
            status=status_code
        )
