# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from powerdns.models import (
    CryptoKey,
    Domain,
    DomainMetadata,
    Record,
    SuperMaster,
)
from rest_framework.filters import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from dnsaas.serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    RecordSerializer,
    SuperMasterSerializer,
)


class FiltersMixin(object):

    filter_backends = (DjangoFilterBackend,)


class DomainViewSet(FiltersMixin, ModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    filter_fields = ('name', 'type')


class RecordViewSet(FiltersMixin, ModelViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_fields = ('name', 'type', 'content', 'domain')


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
