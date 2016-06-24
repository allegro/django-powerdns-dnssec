
"""Views and viewsets for DNSaaS API"""
import django_filters
import logging

from django.core.urlresolvers import reverse
from django.db.models import Q

from powerdns.models import (
    CryptoKey,
    DeleteRequest,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordTemplate,
    RecordRequest,
    SuperMaster,
)
from rest_framework import status
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from .serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordRequestSerializer,
    RecordSerializer,
    RecordTemplateSerializer,
    SuperMasterSerializer,
    TsigKeysTemplateSerializer,
)
from powerdns.utils import to_reverse
from powerdns.models.tsigkeys import TsigKey


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self._set_owner(request.data.copy())
        )
        serializer.is_valid(raise_exception=True)

        record_request = RecordRequest()
        record_request.copy_records_data(serializer.validated_data.items())
        record_request.owner = request.user
        record_request.target_owner = serializer.validated_data['owner']

        if serializer.validated_data['domain'].can_auto_accept(
            request.user
        ):
            serializer.instance = record_request.accept()
            data = serializer.data
            code = status.HTTP_201_CREATED
            headers = {}
        else:
            data = {}
            record_request.save()
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

        if (
            serializer.instance.domain.can_auto_accept(request.user) and
            instance.can_auto_accept(request.user)
        ):
            serializer.instance = record_request.accept()
            code = status.HTTP_200_OK
            headers = {}
        else:
            record_request.save()
            code = status.HTTP_202_ACCEPTED
            headers = {
                'Location': reverse(
                    'api:v2:recordrequest-detail',
                    kwargs={'pk': record_request.id},
                )
            }
        return Response(serializer.data, status=code, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

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
        if (
            instance.domain.can_auto_accept(request.user) and
            instance.can_auto_accept(request.user)
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
            a_records = Record.objects.filter(content__in=ips, type='A')
            ptrs = [
                "{1}.{0}".format(*to_reverse(r.content)) for r in a_records
            ]
            queryset = queryset.filter(
                (Q(content__in=[r.content for r in a_records]) & Q(type='A')) |
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
