"""Views and viewsets for DNSaaS API"""
import logging

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from powerdns.models import (
    CryptoKey,
    DeleteRequest,
    Domain,
    DomainMetadata,
    DomainTemplate,
    DomainRequest,
    Record,
    RecordTemplate,
    RecordRequest,
    SuperMaster,
)
from rest_framework import exceptions, status
from rest_framework.filters import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from powerdns.models.powerdns import can_delete, can_edit
from powerdns.models.requests import RequestStates
from powerdns.serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordRequestSerializer,
    RecordSerializer,
    RecordSerializerV2,
    RecordTemplateSerializer,
    SuperMasterSerializer,
    TsigKeysTemplateSerializer,
)
from powerdns.utils import VERSION, to_reverse
from powerdns.models.tsigkeys import TsigKey


log = logging.getLogger(__name__)


class DomainPermission(DjangoObjectPermissions):

    def has_permission(self, request, view):
        if request.method == 'POST' and not request.user.is_superuser:
            return False
        return super().has_permission(request, view)


class FiltersMixin(object):

    filter_backends = (DjangoFilterBackend,)


class OwnerViewSet(FiltersMixin, ModelViewSet):
    """Base view for objects with owner"""

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.validated_data.get('owner') is None:
            serializer.save(owner=self.request.user)
        else:
            object_ = serializer.save()
            object_.email_owner(self.request.user)


class DomainViewSet(OwnerViewSet):

    queryset = Domain.objects.all().select_related('owner')
    serializer_class = DomainSerializer
    filter_fields = ('name', 'type', 'owner',)
    permission_classes = (DomainPermission,)


class RecordRequestsViewSet(ReadOnlyModelViewSet):
    queryset = RecordRequest.objects.all().select_related(
        'owner', 'domain', 'record', 'target_owner',
    )
    filter_fields = ('owner',)
    serializer_class = RecordRequestSerializer


class RecordViewSet(OwnerViewSet):

    queryset = Record.objects.all().select_related('owner', 'domain')
    serializer_class = RecordSerializer
    filter_fields = ('name', 'content', 'domain', 'owner',)
    search_fields = filter_fields

    def get_object(self):
        obj = super().get_object()
        if self.request.version == 'v1':
            if (
                self.request._request.method in ('PATCH', 'PUT') and
                not can_edit(self.request.user, obj)
            ):
                raise exceptions.PermissionDenied(detail='No permission')
            if (
                self.request._request.method == 'DELETE' and
                not can_delete(self.request.user, obj)
            ):
                raise exceptions.PermissionDenied(detail='No permission')
        return obj

    def get_serializer_class(self):
        if self.request.version == 'v1':
            serializer_class = RecordSerializer
        if self.request.version == 'v2':
            serializer_class = RecordSerializerV2
        return serializer_class

    def create(self, request, *args, **kwargs):
        if self.request.version == 'v1':
            return super().create(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record_request = RecordRequest(
            domain_id=serializer.validated_data['domain'],
            owner_id=request.user.id,
        )
        record_request.copy_records_data(serializer.validated_data.items())
        record_request.save()

        if serializer.validated_data['domain'].can_auto_accept(
            request.user
        ):
            serializer.save()
            record_request.record = serializer.instance
            record_request.state = RequestStates.ACCEPTED
            record_request.save()
            data = serializer.data
            code = status.HTTP_201_CREATED
            headers = {}
        else:
            data = {}
            code = status.HTTP_202_ACCEPTED
            headers = {
                'Location': reverse(
                    'recordrequest-detail', kwargs={'pk': record_request.id}
                )
            }
        return Response(data, status=code, headers=headers)

    def update(self, request, *args, **kwargs):
        if self.request.version == 'v1':
            return super().update(request, *args, **kwargs)
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

        record_request = RecordRequest(
            domain_id=serializer.instance.domain_id,
            owner_id=request.user.id,
            record_id=serializer.instance.id,
        )
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
        record_request.save()

        if (
            serializer.instance.domain.can_auto_accept(self.request.user) and
            instance.can_auto_accept(request.user)
        ):
            record_request.accept_and_assign_record()
            code = status.HTTP_200_OK
            headers = {}
        else:
            code = status.HTTP_202_ACCEPTED
            headers = {
                'Location': reverse(
                    'recordrequest-detail', kwargs={'pk': record_request.id}
                )
            }
        return Response(serializer.data, status=code, headers=headers)

    def destroy(self, request, *args, **kwargs):
        if self.request.version == 'v1':
            return super().destroy(request, *args, **kwargs)

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
            owner=self.request.user, target=instance,
        )
        delete_request.save()
        if (
            instance.domain.can_auto_accept(self.request.user) and
            instance.can_auto_accept(request.user)
        ):
            delete_request.accept()
            code = status.HTTP_204_NO_CONTENT
        else:
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


class HomeView(TemplateView):

    """
    Homepage. This page should point user to API or admin site. This package
    will provide some minimal homepage template. The administrators of
    DNSaaS solutions are encouraged however to create their own ones.
    """

    template_name = "powerdns/home.html"

    def get_context_data(self, **kwargs):

        return {
            'version': VERSION,
        }


def accept_request_factory(request_model, model_name=None):
    def result(request, pk):
        request = request_model.objects.get(pk=pk)
        domain = request.accept()
        if model_name:
            return redirect(
                reverse(
                    'admin:powerdns_{}_change'.format(model_name),
                    args=(domain.pk,)
                )
            )
        else:
            return redirect(reverse('admin:index'))
    return result

accept_domain_request = accept_request_factory(DomainRequest, 'domain')
accept_record_request = accept_request_factory(RecordRequest, 'record')
accept_delete_request = accept_request_factory(DeleteRequest)
