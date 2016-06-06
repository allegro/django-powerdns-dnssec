"""Views and viewsets for DNSaaS API"""

from django.db.models import Q

from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    DomainTemplate,
    Record,
    RecordTemplate,
    SuperMaster,
)
from powerdns.models.powerdns import can_delete, can_edit
from rest_framework import exceptions
from rest_framework.filters import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoObjectPermissions

from .serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordSerializer,
    RecordTemplateSerializer,
    SuperMasterSerializer,
    TsigKeysTemplateSerializer,
)
from powerdns.utils import to_reverse
from powerdns.models.tsigkeys import TsigKey


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
    filter_fields = ('name', 'type')
    permission_classes = (DomainPermission,)


class RecordViewSet(OwnerViewSet):

    queryset = Record.objects.all().select_related('owner', 'domain')
    serializer_class = RecordSerializer
    filter_fields = ('name', 'content', 'domain')
    search_fields = filter_fields

    def get_object(self):
        obj = super().get_object()
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
